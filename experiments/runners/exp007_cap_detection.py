"""EXP-007 — CAP and baselines (SIMULATION RESULT, epoch-level channel model).

Each epoch carries M messages of n fragments. Per fragment: loss from the
epoch's channel model, delay = base + Exp(jitter) (+ attack delay); a message
succeeds if ≥ k fragments arrive within the deadline. Common random numbers:
loss/delay draws are generated for n_protect fragments per message and the
first n are used, so all detectors face the same channel realisation.
Thresholds are calibrated on benign calibration sessions only (matched alarm
fraction); attack families are used only for testing.
"""
import json, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np, pandas as pd
from experiments.common import start, finish, load_config, ROOT
from aegis_pq.netmodel import Bernoulli, GilbertElliott
from aegis_pq.detectors import Normaliser, CAP, Shewhart, EWMAPerFeature, CUSUM, Never, AdaptationPolicy


def make_session(cfg, family, seed):
    rng = np.random.default_rng(seed)
    E, M, NP = cfg["epochs_per_session"], cfg["messages_per_epoch"], cfg["n_protect"]
    p0 = rng.uniform(*cfg["benign_ASSUMPTION"]["bernoulli_loss"])
    lost = np.empty((E, M * NP), bool)
    delay = cfg["base_delay_ms"] + rng.exponential(cfg["jitter_mean_ms"], (E, M * NP))
    rej = np.zeros(E)
    attack = np.zeros(E, bool)
    benign = Bernoulli(p0, rng)
    t0 = int(rng.integers(*cfg["test"]["attack_start"])); T = cfg["test"]["attack_epochs"]
    A = cfg["attack_families_ASSUMPTION"].get(family)
    if family == "benign":
        bc = cfg["benign_congestion_ASSUMPTION"]
        cong = GilbertElliott.from_mean_burst(bc["gilbert_loss"], bc["burst"], rng)
        c0 = int(rng.integers(50, E - bc["epochs"] - 1))
    if family in ("A1_burst_jamming", "A5_pulsed"):
        ge = GilbertElliott.from_mean_burst(A["gilbert_loss"], A["burst"], rng)
    episode = np.zeros(E, bool)
    for e in range(E):
        ch = benign
        on = family not in ("benign", "calibration") and t0 <= e < t0 + T
        if family == "benign" and c0 <= e < c0 + bc["epochs"]:
            ch = cong; episode[e] = True
        if on:
            if family == "A1_burst_jamming":
                ch = ge
            elif family == "A2_iid_drop":
                ch = Bernoulli(max(p0, A["bernoulli_loss"]), rng)
            elif family == "A4_slow_ramp":
                ch = Bernoulli(p0 + (A["bernoulli_loss_max"] - p0) * (e - t0 + 1) / T, rng)
            elif family == "A5_pulsed" and ((e - t0) % (A["on"] + A["off"])) < A["on"]:
                ch = ge
            elif family == "A3_delay_injection":
                hit = rng.random(M * NP) < A["fraction"]
                delay[e, hit] += rng.uniform(*A["delay_ms"], hit.sum())
            elif family == "A6_injection_flood":
                rej[e] = A["reject_fraction"]
            attack[e] = True
        lost[e] = ch.lost(M * NP)
    return {"lost": lost, "delay": delay, "rej": rej, "attack": attack, "t0": t0, "episode": episode}


def observe(cfg, S, e, n):
    M, NP, k, D = cfg["messages_per_epoch"], cfg["n_protect"], cfg["k"], cfg["deadline_ms"]
    L = S["lost"][e].reshape(M, NP)[:, :n]
    ok = (~L) & (S["delay"][e].reshape(M, NP)[:, :n] <= D)
    succ = ok.sum(1) >= k
    return np.array([L.mean(), 1 - succ.mean(), S["rej"][e]]), succ


def run_policy(cfg, S, policy, cols=None):
    E = cfg["epochs_per_session"]
    policy.reset()
    out = {"alarm": np.zeros(E, bool), "n": np.zeros(E, int), "deliv": np.zeros(E)}
    for e in range(E):
        n = policy.n
        o, succ = observe(cfg, S, e, n)
        out["n"][e], out["deliv"][e] = n, succ.mean()
        out["alarm"][e] = policy.step(o if cols is None else o[cols])
    return out


def build(name, norm, theta, cfg, alpha=None):
    d = cfg["detectors"]
    if name.startswith("CAP"):
        return CAP(norm, theta, d["CAP"]["alpha"] if alpha is None else alpha)
    return {"Shewhart": lambda: Shewhart(norm, theta), "EWMA": lambda: EWMAPerFeature(norm, theta, d["EWMA"]["lambda"]),
            "CUSUM": lambda: CUSUM(norm, theta, d["CUSUM"]["kappa"]), "static": lambda: Never()}[name]()


def calibrate(cfg, cal, name, cols, alpha):
    obs = [np.array([observe(cfg, S, e, cfg["n_normal"])[0] for e in range(cfg["epochs_per_session"])]) for S in cal]
    floor = np.array(cfg["sigma_floor"])
    if cols is not None:
        obs = [o[:, cols] for o in obs]; floor = floor[cols]
    norm = Normaliser(np.vstack(obs), floor)
    target = cfg["calibration"]["target_alarm_epoch_fraction"]

    def frac(theta):
        a = 0
        for o in obs:
            d = build(name, norm, theta, cfg, alpha); d.reset()
            a += sum(d.update(x) for x in o)
        return a / sum(len(o) for o in obs)
    lo, hi = 1e-3, 1e3
    for _ in range(40):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if frac(mid) > target else (lo, mid)
    return norm, hi, frac(hi)


def evaluate(cfg, sessions, name, norm, theta, hold, cols=None, alpha=None, nfix=None):
    rows = []
    for fam, ss in sessions.items():
        for i, S in enumerate(ss):
            if nfix is not None:
                pol = AdaptationPolicy(Never(), cfg["k"], nfix, nfix, hold)
            else:
                pol = AdaptationPolicy(build(name, norm, theta, cfg, alpha), cfg["k"], cfg["n_normal"], cfg["n_protect"], hold)
            r = run_policy(cfg, S, pol, cols)
            onset = r["alarm"] & ~np.r_[False, r["alarm"][:-1]]
            pre = np.arange(cfg["epochs_per_session"]) < S["t0"]
            if fam == "benign":
                benign_mask, att = ~S["episode"], None
            else:
                benign_mask, att = pre, S["attack"]
            row = {"family": fam, "session": i,
                   "false_onsets_per_1000_benign_epochs": 1000 * onset[benign_mask].sum() / benign_mask.sum(),
                   "mean_n": r["n"].mean(), "delivery_overall": r["deliv"].mean()}
            if fam == "benign":
                row["alarm_in_congestion_episode"] = bool(r["alarm"][S["episode"]].any())
            else:
                hit = np.flatnonzero(r["alarm"] & att)
                row["detected"] = len(hit) > 0
                row["delay_epochs"] = (hit[0] - S["t0"]) if len(hit) else np.nan
                row["delivery_under_attack"] = r["deliv"][att].mean()
            rows.append(row)
    return rows


def main(path):
    cfg = load_config(path)
    run = start(cfg["exp_id"], cfg)
    cal = [make_session(cfg, "calibration", cfg["calibration"]["seed_base"] + i) for i in range(cfg["calibration"]["sessions"])]
    fams = ["benign"] + list(cfg["attack_families_ASSUMPTION"])
    test = {f: [make_session(cfg, f, cfg["test"]["seed_base"] + 1000 * j + i) for i in range(cfg["test"]["sessions_per_family"])]
            for j, f in enumerate(fams)}
    hold = cfg["hold_epochs"]
    variants = [("CAP", "CAP", None, None, hold), ("EWMA", "EWMA", None, None, hold), ("CUSUM", "CUSUM", None, None, hold),
                ("Shewhart", "Shewhart", None, None, hold)]
    variants += [(f"CAP_alpha={a}", "CAP", None, a, hold) for a in cfg["ablations"]["CAP_alpha"]]
    variants += [("CAP_no_hysteresis", "CAP", None, None, cfg["ablations"]["CAP_no_hysteresis"]["hold_epochs"]),
                 ("CAP_loss_only", "CAP", cfg["ablations"]["CAP_loss_only"]["observables"], None, hold)]
    allrows, calrows = [], []
    for label, name, cols, alpha, h in variants:
        norm, theta, fr = calibrate(cfg, cal, name, cols, alpha)
        calrows.append({"variant": label, "theta": theta, "calibration_alarm_fraction": fr,
                        "mu": norm.mu.tolist(), "sigma": norm.sd.tolist()})
        for r in evaluate(cfg, test, name, norm, theta, h, cols, alpha):
            r["variant"] = label; allrows.append(r)
        print("done", label, round(theta, 3), fr, flush=True)
    for nfix in (cfg["n_normal"], cfg["n_protect"]):
        for r in evaluate(cfg, test, "static", None, None, hold, nfix=nfix):
            r["variant"] = f"static_n={nfix}"; allrows.append(r)
    R = pd.DataFrame(allrows)
    R.to_csv(os.path.join(run, "per_session.csv"), index=False)
    pd.DataFrame(calrows).to_csv(os.path.join(run, "calibration.csv"), index=False)
    agg = R.groupby(["variant", "family"]).agg(
        sessions=("session", "size"), detection_rate=("detected", "mean"), delay_median=("delay_epochs", "median"),
        delay_mean=("delay_epochs", "mean"), delivery_under_attack=("delivery_under_attack", "mean"),
        false_onsets_per_1000=("false_onsets_per_1000_benign_epochs", "mean"), mean_n=("mean_n", "mean"),
        congestion_alarm_rate=("alarm_in_congestion_episode", "mean")).reset_index()
    agg.to_csv(os.path.join(run, "summary.csv"), index=False)
    # θ sensitivity for CAP (descriptive; operating point fixed by calibration above)
    norm, _, _ = calibrate(cfg, cal, "CAP", None, None)
    sw = []
    for th in cfg["theta_sweep_CAP"]:
        R2 = pd.DataFrame(evaluate(cfg, test, "CAP", norm, th, hold))
        att = R2[R2.family != "benign"]
        sw.append({"theta": th, "detection_rate_all_attacks": att.detected.mean(),
                   "median_delay_epochs": att.delay_epochs.median(),
                   "false_onsets_per_1000_benign": R2[R2.family == "benign"].false_onsets_per_1000_benign_epochs.mean(),
                   "mean_n_benign": R2[R2.family == "benign"].mean_n.mean()})
    pd.DataFrame(sw).to_csv(os.path.join(run, "theta_sweep_cap.csv"), index=False)
    finish(run)
    print(run)
    print(agg.round(3).to_string()); print(pd.DataFrame(calrows)[["variant", "theta", "calibration_alarm_fraction"]])
    print(pd.DataFrame(sw).round(3).to_string())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "experiments", "configs", "EXP-007_cap_detection.json"))
