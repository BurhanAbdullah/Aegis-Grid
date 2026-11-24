"""EXP-003 — delivery probability, redundancy cost and security/availability
trade-off of fragment-level all-or-nothing reconstruction.

Part A (SIMULATION RESULT, count-based Monte Carlo): for each (k, n) code and
loss model, send `trials` consecutive messages of n packets over a channel whose
state persists between messages; a message is delivered iff ≥ k of its n packets
arrive. 95 % Wilson score intervals. Bernoulli cases are also compared with the
closed form P = Σ_{j≥k} C(n,j)(1−p)^j p^(n−j) (ANALYTICALLY DERIVED).

Part B (SIMULATION RESULT, full implementation): the same quantity measured by
pushing real AGP/1 records (ML-KEM/ML-DSA session, AONT, RS, AES-GCM) through
the loss model into the real receiver, to validate Part A's abstraction.

Part C (ANALYTICALLY DERIVED from the implementation's sizes): bytes on the wire
per message and the adversary thresholds (captures needed = k; drops needed to
deny = n − k + 1).
"""
import csv, json, math, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np
from experiments.common import start, finish, load_config, ROOT
from aegis_pq.netmodel import Bernoulli, GilbertElliott, Multipath


def wilson(s, n, z=1.959963984540054):
    if n == 0:
        return (float("nan"),) * 2
    p = s / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def analytic(k, n, p):
    return sum(math.comb(n, j) * (1 - p) ** j * p ** (n - j) for j in range(k, n + 1))


def channel(kind, loss, burst, rng, paths):
    if kind == "bernoulli":
        return Bernoulli(loss, rng)
    if kind == "gilbert":
        return GilbertElliott.from_mean_burst(loss, burst, rng)
    if kind == "gilbert_2path":
        return Multipath([GilbertElliott.from_mean_burst(loss, burst, rng) for _ in range(paths)])
    raise ValueError(kind)


def part_a(cfg, run):
    rows, idx = [], 0
    cases = [("bernoulli", p, 1) for p in cfg["bernoulli_p"]]
    for kind in ("gilbert", "gilbert_2path"):
        cases += [(kind, l, b) for l in cfg["gilbert_mean_loss"] for b in cfg["gilbert_mean_burst"]]
    T = cfg["trials"]
    for (k, n) in cfg["codes"]:
        for kind, loss, burst in cases:
            seed = cfg["base_seed"] + idx; idx += 1
            rng = np.random.default_rng(seed)
            ch = channel(kind, loss, burst, rng, cfg["multipath_paths"])
            lost = ch.lost(T * (n + cfg["inter_message_gap_packets"])).reshape(T, -1)[:, :n]
            recv = n - lost.sum(axis=1)
            s = int((recv >= k).sum())
            lo, hi = wilson(s, T)
            rows.append({"k": k, "n": n, "model": kind, "mean_loss": loss, "mean_burst": burst, "seed": seed,
                         "trials": T, "delivered": s, "p_delivery": s / T, "ci95_lo": lo, "ci95_hi": hi,
                         "observed_packet_loss": float(lost.mean()),
                         "analytic_iid": analytic(k, n, loss) if kind == "bernoulli" else ""})
    with open(os.path.join(run, "delivery_montecarlo.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows


def part_b(cfg, run):
    from aegis_pq.clock import ManualClock
    from aegis_pq.pki import GridCA
    from aegis_pq.handshake import Initiator, Responder, run_handshake
    from aegis_pq.channel import SecureChannel, ChannelConfig
    from aegis_pq.pipeline import Sender, Receiver, body_size_for
    pv = cfg["pipeline_validation"]
    out = []
    for j, (kind, loss, burst, (k, n)) in enumerate(pv["cases"]):
        seed = cfg["base_seed"] + 100000 + j
        rng = np.random.default_rng(seed)
        clock = ManualClock()
        ca = GridCA(now_ms=clock.now_ms())
        ik, rk = run_handshake(Initiator("cc-01", "rtu-07", [ca.issue("cc-01", now_ms=clock.now_ms())], ca.cert, clock),
                               Responder("rtu-07", [ca.issue("rtu-07", now_ms=clock.now_ms())], ca.cert, clock))
        cc = ChannelConfig(body_size=body_size_for(pv["message_bytes"], k))
        snd, rcv = Sender(SecureChannel(ik, clock, cc), k, n), Receiver(SecureChannel(rk, clock, cc))
        ch = channel(kind, loss, burst, rng, 2)
        delivered = 0
        for _ in range(pv["messages"]):
            m = rng.bytes(pv["message_bytes"])
            mid, recs = snd.seal_message(m, 1000)
            mask = ch.lost(n)
            got = None
            for rec, l in zip(recs, mask):
                if not l:
                    g = rcv.receive(rec)
                    got = g or got
            if got is not None:
                assert got == (mid, m), "delivered wrong message"
                delivered += 1
            else:
                rcv.expire(mid)
        lo, hi = wilson(delivered, pv["messages"])
        out.append({"model": kind, "mean_loss": loss, "mean_burst": burst, "k": k, "n": n, "seed": seed,
                    "messages": pv["messages"], "delivered": delivered, "p_delivery": delivered / pv["messages"],
                    "ci95_lo": lo, "ci95_hi": hi,
                    "receiver_rejects": {r.value: c for r, c in rcv.rejects.items()}})
    json.dump(out, open(os.path.join(run, "pipeline_validation.json"), "w"), indent=2)
    return out


def part_c(cfg, run):
    from aegis_pq.pipeline import body_size_for, record_size
    from aegis_pq.channel import INNER
    rows = []
    for L in cfg["overhead_message_bytes"]:
        single = record_size(INNER.size + L)          # one AEAD record carrying M, no AONT/fragmentation
        for (k, n) in cfg["codes"]:
            rs = record_size(body_size_for(L, k))
            rows.append({"message_bytes": L, "k": k, "n": n, "record_bytes": rs, "bytes_per_message": n * rs,
                         "single_record_bytes": single, "expansion_vs_single_record": n * rs / single,
                         "redundancy_n_over_k": n / k, "captures_needed_by_adversary": k,
                         "drops_needed_to_deny": n - k + 1, "max_losses_tolerated": n - k})
    with open(os.path.join(run, "overhead_and_thresholds.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def main(path):
    cfg = load_config(path)
    run = start(cfg["exp_id"], cfg)
    a = part_a(cfg, run)
    b = part_b(cfg, run)
    part_c(cfg, run)
    # consistency check between Part B (real pipeline) and Part A abstraction for identical settings
    checks = []
    for r in b:
        match = [x for x in a if x["k"] == r["k"] and x["n"] == r["n"] and x["model"] == r["model"]
                 and x["mean_loss"] == r["mean_loss"] and (r["model"] == "bernoulli" or x["mean_burst"] == r["mean_burst"])]
        if match:
            m = match[0]
            overlap = not (r["ci95_hi"] < m["ci95_lo"] or m["ci95_hi"] < r["ci95_lo"])
            checks.append({"case": f'{r["model"]} loss={r["mean_loss"]} burst={r["mean_burst"]} k={r["k"]} n={r["n"]}',
                           "pipeline": r["p_delivery"], "montecarlo": m["p_delivery"], "ci_overlap": overlap})
    json.dump(checks, open(os.path.join(run, "abstraction_check.json"), "w"), indent=2)
    finish(run, note=f"abstraction checks overlapping: {sum(c['ci_overlap'] for c in checks)}/{len(checks)}")
    print(run); print(json.dumps(checks, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "experiments", "configs", "EXP-003_reliability.json"))
