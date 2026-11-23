"""EXP-004 — partial-capture leakage (SIMULATION RESULT).

Adversary model: records were captured and the session key was later exposed,
so the adversary sees fragment *contents* for the fragments it captured, but it
captured only k−1 of them (one fewer than needed).

Metric: fraction of plaintext bytes the adversary's best simple reconstruction
gets right.  For random 256-byte messages, chance level is 1/256 ≈ 0.0039.
 * legacy XOR transform (legacy/core/fragmentation.py): adversary holds the pad
   fragment and all masked fragments except one (N−1 of N).
 * AONT + RS(k,n): adversary holds k−1 shards; fills the missing shard with
   zeros, RS-decodes, inverts the AONT ignoring the integrity check.
The AONT result is bounded analytically by q·2^(−8f) (f = shard bytes) under
the random-oracle model; the simulation only illustrates it and cannot prove it.
"""
import csv, hashlib, json, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np
from experiments.common import start, finish, load_config, ROOT
from aegis_pq import aont, erasure
from legacy.core.fragmentation import aont_fragment          # legacy construction under audit


def main(path):
    cfg = load_config(path)
    run = start(cfg["exp_id"], cfg)
    rng = np.random.default_rng(cfg["seed"])
    L, T = cfg["message_bytes"], cfg["trials"]
    rows = []
    for N in cfg["legacy_N"]:
        fr = []
        for _ in range(T):
            m = rng.bytes(L)
            frags = aont_fragment(m, N)
            K = frags[-1]
            miss = int(rng.integers(0, N - 1))
            off, ok = 0, 0
            for i, f in enumerate(frags[:-1]):
                if i != miss:
                    ok += sum(a == b for a, b in zip(bytes(x ^ y for x, y in zip(f, K[off:off + len(f)])), m[off:off + len(f)]))
                off += len(f)
            fr.append(ok / L)
        fr = np.array(fr)
        rows.append({"scheme": "legacy XOR transform", "k": N, "n": N, "fragments_held": N - 1, "trials": T,
                     "mean_fraction_bytes_recovered": fr.mean(), "std": fr.std(ddof=1),
                     "max": fr.max(), "chance_level": 1 / 256})
    for k, n in cfg["codes"]:
        fr = []
        for _ in range(T):
            m = rng.bytes(L)
            y = aont.transform(m)
            sh = erasure.encode(y, k, n)
            held = rng.choice(n, size=k - 1, replace=False)
            missing = [i for i in range(n) if i not in set(held.tolist())][0]
            guess = {int(i): sh[int(i)] for i in held}
            guess[missing] = b"\x00" * len(sh[0])
            yy = erasure.decode(guess, k, n, len(y))
            c, t = yy[:-32], yy[-32:]
            kk = bytes(a ^ b for a, b in zip(t, hashlib.sha256(c).digest()))
            x = aont._ctr(kk, c)[4:4 + L]
            fr.append(sum(a == b for a, b in zip(x, m)) / L)
        fr = np.array(fr)
        rows.append({"scheme": "package-transform AONT + RS", "k": k, "n": n, "fragments_held": k - 1, "trials": T,
                     "mean_fraction_bytes_recovered": fr.mean(), "std": fr.std(ddof=1),
                     "max": fr.max(), "chance_level": 1 / 256,
                     "shard_bytes": len(erasure.encode(aont.transform(b"\0" * L), k, n)[0])})
    with open(os.path.join(run, "partial_capture.csv"), "w", newline="") as f:
        keys = sorted({k for r in rows for k in r}, key=lambda s: list(rows[-1]).index(s) if s in rows[-1] else 99)
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    finish(run)
    print(run)
    for r in rows:
        print(r["scheme"], r["k"], r["n"], round(r["mean_fraction_bytes_recovered"], 4), round(r["max"], 4))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "experiments", "configs", "EXP-004_partial_capture.json"))
