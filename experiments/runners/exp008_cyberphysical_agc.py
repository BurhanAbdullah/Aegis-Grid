"""EXP-008 — cyber-physical fail-secure study on the IEEE 14-bus dynamic case
(SIMULATION RESULT; plant model Andes 2.0.0, communication = real AGP/1 objects).

Control loop: every T_agc the control centre computes ACE = β·Δω (pu, single
balancing area; tie-lines ignored), integrates P_agc ← P_agc − Ki·T_agc·ACE,
and sends each of the 5 plants its share P_agc/5 as a command. Commands are
sealed with AGP/1 (ML-KEM-768/ML-DSA-65 session per plant, RS(5,7) fragments,
deadline field) and opened by the plant receiver with a clock synchronised to
simulation time. TGOV1 input: paux = ΔP·R (Andes TGOV1 adds paux before the
1/R gain).

Receivers
  secure_failsecure    AGP/1 Receiver; command applied only if authentic,
                       fresh, not replayed and reconstructed before its
                       deadline; otherwise U_safe = hold the last validated
                       set-point (primary droop stays active).
  insecure_accept_all  plaintext commands, no authentication/replay/deadline
                       checks (baseline); applies whatever arrives last.
Attacks (in the window [attack_start, attack_start+duration))
  drop    every command dropped            delay   commands delivered delay_s late
  replay  commands recorded at t < ramp_start replayed in place of fresh ones
  forge   attacker injects its own command (−0.15 pu per plant); real ones dropped
"""
import json, os, struct, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np, pandas as pd
import andes
from experiments.common import start, finish, load_config, ROOT
from aegis_pq.channel import ChannelConfig, SecureChannel
from aegis_pq.clock import ManualClock
from aegis_pq.handshake import Initiator, Responder, run_handshake
from aegis_pq.pipeline import Sender, Receiver, body_size_for
from aegis_pq.pki import GridCA

CMD = struct.Struct(">Id")              # plant, delta_pu
andes.config_logger(stream_level=40)


class SecureLink:
    def __init__(self, ca, cc, plant_cred, clock, k, n):
        ki, kr = run_handshake(Initiator("cc-01", plant_cred.identity, [cc], ca.cert, clock),
                               Responder(plant_cred.identity, [plant_cred], ca.cert, clock))
        cfg = ChannelConfig(body_size=body_size_for(CMD.size, k))
        self.tx = Sender(SecureChannel(ki, clock, cfg), k, n)
        self.rx = Receiver(SecureChannel(kr, clock, cfg))

    def send(self, plant, val, deadline_ms):
        return self.tx.seal_message(CMD.pack(plant, val), deadline_ms)[1]

    def deliver(self, records):
        out = None
        for r in records:
            got = self.rx.receive(r)
            if got is not None:
                out = CMD.unpack(got[1])[1]
        return out


class InsecureLink:
    def send(self, plant, val, deadline_ms):
        return [CMD.pack(plant, val)]

    def deliver(self, records):
        out = None
        for r in records:
            if len(r) == CMD.size:
                out = CMD.unpack(r)[1]
        return out


def simulate(cfg, sc, receiver, pki):
    ss = andes.load(andes.get_case(cfg["case"]), setup=False, no_output=True, default_config=True)
    ss.PQ.config.p2p = 1; ss.PQ.config.p2z = 0; ss.PQ.config.q2q = 1; ss.PQ.config.q2z = 0
    ss.setup(); ss.PFlow.run(); ss.TDS.config.no_tqdm = 1
    ss.TDS.config.tf = 0.5; ss.TDS.init(); ss.TDS.run()
    gov = list(ss.TGOV1.idx.v); R = np.array(ss.TGOV1.R.v)
    p0 = np.array(ss.PQ.Ppf.v, float); share = p0 / p0.sum()
    clock = ManualClock()
    t_base = clock.t_ms
    ca, cc, plants = pki
    links = [SecureLink(ca, cc, plants[i], clock, cfg["k"], cfg["n"]) if receiver == "secure_failsecure" else InsecureLink()
             for i in range(len(gov))]
    applied = np.zeros(len(gov)); pagc = 0.0
    T, ki, beta = cfg["agc_period_s"], cfg["agc_ki_per_s"], cfg["bias_beta_pu"]
    a0, a1 = cfg["attack_start_s"], cfg["attack_start_s"] + sc["duration_s"]
    recorded, delayed, log = [[] for _ in gov], [], []
    accepted = rejected = 0
    acked_prev = True
    t = 0.5
    while t < cfg["t_end_s"] - 1e-9:
        t_next = round(t + T, 6)
        clock.t_ms = t_base + t * 1000
        w = float(np.mean(ss.GENROU.omega.v))
        ace = beta * (w - 1.0)
        # anti-windup option: integrate only if every plant acknowledged the previous command
        # (acknowledgement = the plant accepted a valid, fresh command in the previous round;
        # the acknowledgement path is assumed to be authenticated and subject to the same attack)
        if not cfg.get("anti_windup", False) or acked_prev:
            pagc -= ki * T * ace
        attack_on = sc["attack"] != "none" and a0 <= t < a1
        inbox = [[] for _ in gov]
        for i, L in enumerate(links):
            recs = L.send(i, pagc / len(gov), cfg["command_deadline_ms"])
            if t < cfg["ramp_start_s"]:
                recorded[i].append(recs)
            if not attack_on:
                inbox[i] += recs
            elif sc["attack"] == "delay":
                delayed.append((t + sc["delay_s"], i, recs))
            elif sc["attack"] == "replay":
                inbox[i] += recorded[i][int(t / T) % len(recorded[i])]
            elif sc["attack"] == "forge":
                if receiver == "secure_failsecure":
                    inbox[i].append(os.urandom(len(recs[0])))      # no key: best effort is random/garbled records
                    inbox[i].append(recs[0][:-1] + bytes([recs[0][-1] ^ 1]))
                else:
                    inbox[i].append(CMD.pack(i, sc["forged_delta_pu_per_plant"]))
        for (td, i, recs) in [d for d in delayed if d[0] <= t]:
            inbox[i] += recs
        delayed = [d for d in delayed if d[0] > t]
        acked_now = [False] * len(links)
        for i, L in enumerate(links):
            if not inbox[i]:
                continue
            v = L.deliver(inbox[i])
            if v is not None and abs(v - pagc / len(gov)) < 1e-12:
                acked_now[i] = True
            if v is not None:
                applied[i] = v; accepted += 1
            else:
                rejected += 1
        acked_prev = all(acked_now)
        ss.TGOV1.set(src="paux0", idx=gov, attr="v", value=list(applied * R))
        # load ramp, applied at the AGC instants
        dP = max(0.0, (t - cfg["ramp_start_s"])) * sc["ramp_pu_per_min"] / 60.0
        ss.PQ.set(src="Ppf", idx=list(ss.PQ.idx.v), attr="v", value=list(p0 + share * dP))
        ss.TDS.config.tf = t_next; ss.TDS.run()
        if ss.exit_code != 0:
            raise RuntimeError("TDS failed at t=%g" % t_next)
        om = np.array(ss.GENROU.omega.v)
        log.append({"t_s": t_next, "f_hz": float(np.mean(om)) * cfg["limits_ASSUMPTION"]["f_nominal_hz"],
                    "pagc_cmd_pu": pagc, "applied_sum_pu": float(applied.sum()), "load_delta_pu": dP,
                    "pm_sum_pu": float(np.sum(ss.TGOV1.pout.v)), "attack": attack_on,
                    "gov_at_limit": int(np.sum(np.isclose(ss.TGOV1.pout.v, ss.TGOV1.VMAX.v, atol=1e-4) |
                                               np.isclose(ss.TGOV1.pout.v, ss.TGOV1.VMIN.v, atol=1e-4)))})
        t = t_next
    rej = {}
    if receiver == "secure_failsecure":
        for L in links:
            for k_, v in L.rx.rejects.items():
                rej[getattr(k_, "name", str(k_))] = rej.get(getattr(k_, "name", str(k_)), 0) + v
    return pd.DataFrame(log), accepted, rejected, rej, float(np.sum(1.0 / R))


def main(path):
    cfg = load_config(path)
    run = start(cfg["exp_id"], cfg)
    clk = ManualClock()
    ca = GridCA(now_ms=clk.now_ms(), days=3650)
    cc = ca.issue("cc-01", now_ms=clk.now_ms(), valid_s=10 ** 7)
    plants = [ca.issue(f"plant-{i+1}", now_ms=clk.now_ms(), valid_s=10 ** 7) for i in range(5)]
    lim = cfg["limits_ASSUMPTION"]; f0 = lim["f_nominal_hz"]
    rows, ts = [], []
    for sc in cfg["scenarios"]:
        for rcv in cfg["receivers"]:
            if sc["attack"] == "none" and rcv != cfg["receivers"][0]:
                continue
            df, acc, rj, rej, droop = simulate(cfg, sc, rcv, (ca, cc, plants))
            df["scenario"], df["receiver"] = sc["name"], rcv
            ts.append(df)
            dev = df.f_hz - f0
            post = df[df.t_s >= cfg["attack_start_s"]]
            out_ss = post[(post.f_hz - f0).abs() > lim["steady_state_band_hz"]]
            row = {"scenario": sc["name"], "receiver": rcv, "attack": sc["attack"], "duration_s": sc["duration_s"],
                   "ramp_pu_per_min": sc["ramp_pu_per_min"], "f_min_hz": df.f_hz.min(), "f_max_hz": df.f_hz.max(),
                   "max_abs_dev_hz": dev.abs().max(),
                   "time_outside_ss_band_s": len(out_ss) * cfg["agc_period_s"],
                   "first_ss_violation_after_attack_start_s": (out_ss.t_s.iloc[0] - cfg["attack_start_s"]) if len(out_ss) else None,
                   "instantaneous_band_violated": bool((dev.abs() > lim["instantaneous_band_hz"]).any()),
                   "max_govs_at_limit": int(df.gov_at_limit.max()),
                   "commands_accepted": acc, "rounds_with_only_invalid_records": rj, "receiver_rejects": json.dumps(rej)}
            if sc["attack"] == "drop":
                # ANALYTICALLY DERIVED: with set-points held and constant-power load, the quasi-steady
                # deviation grows as Δf = −f0·r·τ/(Σ1/R); time to reach the band:
                row["analytic_hold_time_to_band_s"] = lim["steady_state_band_hz"] / f0 * droop / (sc["ramp_pu_per_min"] / 60.0)
            rows.append(row)
            print(sc["name"], rcv, round(row["max_abs_dev_hz"], 4), row["first_ss_violation_after_attack_start_s"], rej, flush=True)
    pd.concat(ts).to_csv(os.path.join(run, "timeseries.csv.gz"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(run, "summary.csv"), index=False)
    finish(run)
    print(run)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "experiments", "configs", "EXP-008_cyberphysical_agc.json"))
