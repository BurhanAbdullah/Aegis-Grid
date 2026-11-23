"""EXP-001: audit probes of the legacy implementation (main@65f83bf).

Each probe tests one manuscript claim against the code that actually exists.
Probes only *read* legacy modules and stored CSVs; nothing is modified.
Run:  python3 scripts/research_integrity/audit_probes.py
Output: results/raw/EXP-001_audit_probes/probes.json
"""
import csv, json, os, random, sys, subprocess, platform
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from core.fragmentation import aont_fragment, aont_reconstruct  # legacy code under audit

OUT = "results/raw/EXP-001_audit_probes"
SEED = 20261123
rng = random.Random(SEED)
res = {"seed": SEED, "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
       "python": platform.python_version()}

# --- Probe 1: does the legacy "XOR-AONT" leak plaintext from a strict subset? -----------
# Adversary holds the key fragment K and all masked fragments except one.
trials, leaked_fraction = 2000, []
for _ in range(trials):
    n = rng.choice([5, 10, 20, 30])
    msg = bytes(rng.getrandbits(8) for _ in range(256))
    frags = aont_fragment(msg, n)
    miss = rng.randrange(0, n - 1)            # drop one *masked* fragment (not K)
    K = frags[-1]
    # recover every byte whose masked fragment was captured
    off, recovered, total_known = 0, 0, 0
    for i, f in enumerate(frags[:-1]):
        if i != miss:
            rec = bytes(a ^ b for a, b in zip(f, K[off:off + len(f)]))
            recovered += sum(1 for a, b in zip(rec, msg[off:off + len(f)]) if a == b)
        off += len(f)
    leaked_fraction.append(recovered / len(msg))
res["probe1_xor_transform_partial_recovery"] = {
    "setup": "256-byte uniform message, N in {5,10,20,30}, adversary misses exactly one masked fragment but holds K",
    "trials": trials,
    "mean_fraction_of_plaintext_bytes_recovered": sum(leaked_fraction) / trials,
    "min_fraction": min(leaked_fraction), "max_fraction": max(leaked_fraction),
    "interpretation": "A strict subset of fragments reveals most plaintext bytes; the construction is not an AONT.",
}
# Converse: missing only K leaks nothing (one-time pad) -- record for completeness
res["probe1b_missing_only_key_fragment"] = "masked fragments alone are a one-time-pad encryption of M; no bytes recoverable without K (by construction, not measured)"

# Reconstruction-order bug check: aont_reconstruct assumes K is last and fragments are in order
msg = b"POWER_GRID_CMD"
fr = aont_fragment(msg, 5)
shuffled = fr[1:] + fr[:1]
res["probe1c_reordered_fragments_decode_correctly"] = aont_reconstruct(shuffled) == msg
# data shorter than N-1 produces empty fragments
fr = aont_fragment(msg, 30)
res["probe1d_empty_fragments_for_14B_message_N30"] = sum(1 for f in fr if len(f) == 0)

# --- Probe 2: is stochastic_loss.csv a Markov (Gilbert-Elliott) burst model? -------------
stored = {}
with open("paper_artifacts/journal_data/stochastic_loss.csv") as f:
    for r in csv.DictReader(f):
        stored[float(r["state_transition_prob"])] = float(r["success_rate"])
res["probe2_stochastic_loss_vs_iid"] = {
    p: {"stored": v, "iid_analytic_(1-p)^20": (1 - p) ** 20,
        "z_score_vs_iid_(n=2000)": ((v - (1 - p) ** 20) / (((1 - p) ** 20 * (1 - (1 - p) ** 20) / 2000) ** 0.5))}
    for p, v in stored.items()}
res["probe2_note"] = ("paper_artifacts/journal_scripts/stochastic_loss.sh draws the channel state independently "
                      "at every step (state does not depend on the previous state), i.e. i.i.d. Bernoulli loss; "
                      "stored values are within |z|<2 of (1-p)^20 for all four p values (see z_score).")

# --- Probe 3: Monte Carlo CI file -------------------------------------------------------
rows = list(csv.DictReader(open("paper_artifacts/journal_data/monte_carlo_ci.csv")))
res["probe3_monte_carlo_ci"] = {
    "N_values_in_file": sorted({int(r["N"]) for r in rows}),
    "rows": len(rows),
    "rows_with_negative_lower_ci": sum(1 for r in rows if float(r["lower_ci"]) < 0),
    "rows_with_zero_width_ci_but_mean_not_0_or_1": sum(1 for r in rows if float(r["lower_ci"]) == float(r["upper_ci"]) and 0 < float(r["mean"]) < 1),
    "rows_with_mean_0_and_zero_width": sum(1 for r in rows if float(r["mean"]) == 0.0),
    "ci_method": "Wald normal approximation 1.96*std/sqrt(n); script uses unseeded random()",
}

# --- Probe 4: provenance of the 48 ms / 35 ms latency numbers --------------------------
plotted = list(csv.DictReader(open("paper_artifacts/data/v3_latency_comparison.csv")))
res["probe4_latency_csv"] = {
    "plotted_static_max_ms": max(float(r["static"]) for r in plotted),
    "plotted_agent_max_ms": max(float(r["agent"]) for r in plotted),
    "generator_script": "scripts/gen_v3_latency_compare_csv.py writes constant static=48, agent=35 for every load",
    "generator_for_plotted_csv": "none found in any branch",
}
os.makedirs(OUT, exist_ok=True)
json.dump(res, open(f"{OUT}/probes.json", "w"), indent=2, default=str)
print(json.dumps(res, indent=2, default=str))
