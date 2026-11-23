# Experiment Register

Permanent record. Failed experiments are never deleted. Hypotheses are written
before execution. Commit = the commit whose code produced the result (for
EXP-000/001 the audited legacy code is `65f83bf`; the probe scripts themselves
are committed on `research-integrity-remediation`).

---

## EXP-000 — Execute legacy entry points
- **Research question:** Do the repository's existing entry points and tests run on main@65f83bf?
- **Hypothesis (pre-run):** Some legacy scripts will fail because of API drift between files.
- **Method:** `scripts/research_integrity/run_legacy_entrypoints.sh` runs 8 commands with a 300 s timeout and records true exit status.
- **Configuration / seed:** none (legacy code is unseeded).
- **Environment:** see `results/raw/EXP-000_legacy_entrypoints/environment.txt` (Python 3.13.18, pycryptodome 3.23.0, Linux x86_64).
- **Date:** 2026-11-23
- **Result path:** `results/raw/EXP-000_legacy_entrypoints/`
- **Outcome:** 2 of 8 exit 0 (`main.py`, `verify_model.py`); 6 fail (3 legacy verify scripts, `generate_validation.py`, pytest finds no tests, `get_layer_key` TypeError).
- **Interpretation:** No working automated test of any research claim exists. Label: VERIFIED (re-executed).
- **Manuscript relevance:** Reproducibility claims (R2).

## EXP-001 — Audit probes of legacy claims
- **Research question:** Do the legacy fragmentation code and stored CSVs support the manuscript's AONT, Markov-loss, Monte-Carlo and latency claims?
- **Hypotheses (pre-run):** (a) the XOR transform reveals plaintext from strict subsets; (b) the "Markov" data equal i.i.d. predictions; (c) the CI file uses an invalid interval method; (d) latency values trace to constants.
- **Method:** `python3 scripts/research_integrity/audit_probes.py` (seed 20261123; 2000 trials for probe 1).
- **Result path:** `results/raw/EXP-001_audit_probes/probes.json`
- **Outcome:** (a) confirmed — mean 88.4 % (min 75 %, max 96.9 %) of plaintext bytes recovered when one masked fragment is missing; reordered fragments decode incorrectly; 28/30 fragments empty for a 14-byte message. (b) confirmed — |z| < 2 vs (1−p)^20 for all four transition probabilities; script draws state independently each step. (c) confirmed — 3 negative lower bounds, 10 zero-width intervals at mean 0. (d) confirmed — generator writes 48/35 constants; plotted CSV (max 56/33) has no generator.
- **Interpretation:** Manuscript claims C5, C11, C12, C3 are not supported by the legacy code. Label: SIMULATION RESULT (probe 1) / CODE INSPECTION (b–d).
- **Manuscript relevance:** R2 points on AONT, evaluation, reproducibility.
