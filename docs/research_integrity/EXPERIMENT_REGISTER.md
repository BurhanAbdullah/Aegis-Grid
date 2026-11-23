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

## EXP-002 — Cryptographic and handshake CPU cost
- **Research question:** What CPU time and wire size does each AGP/1 operation and the complete handshake cost on the available machine?
- **Hypothesis (pre-run):** Full handshake CPU cost (both parties) is in the low milliseconds on x86-64 and dominated by ML-DSA signing; per-record AEAD cost is in microseconds.
- **Method:** `python3 experiments/runners/exp002_crypto_bench.py experiments/configs/EXP-002_crypto_bench.json`; `perf_counter_ns`, warm-up 50, GC disabled during timing; 5000 samples (fast ops), 1000 (keygen/sign/cert validation), 300 handshakes per suite.
- **Seed:** not applicable (keys from OS CSPRNG; timing study).
- **Environment:** `environment.json` in run directory (Python 3.13.18, cryptography 50.0.1, OpenSSL 3.5.9, Intel Xeon 2.1 GHz VM).
- **Result path:** `results/raw/EXP-002/run_20261123T165540Z/` (development run, uncommitted working tree — `git_dirty: true`). Superseded for the manuscript by the frozen run in Milestone 7.
- **Outcome (dev run, medians):** ML-KEM-768 encaps 39 µs / decaps 36 µs; ML-DSA-65 sign 786 µs (p99 3786 µs, rejection-sampling tail) / verify 189 µs; AES-256-GCM 1 KiB ≈0.8 µs; record seal/open 3–7 µs; full handshake 3.4–4.7 ms CPU; handshake wire size 17.0–24.8 kB.
- **Interpretation:** Handshake cost is small relative to a 50–100 ms budget on this machine but exceeds a 3 ms protection budget by itself; embedded devices were not measured.
- **Manuscript relevance:** R1 (PQC benchmarks, handshake overhead), R2 (protocol costs).

## EXP-003 — Delivery probability under i.i.d. and burst loss
- **Research question:** How does the probability that a message is reconstructed depend on (k, n), loss rate and burstiness, and does erasure coding or two-path transmission help?
- **Hypothesis (pre-run):** k = n delivery decays as (1−p)^n under i.i.d. loss; burst loss at equal mean rate changes the decay; k < n restores delivery under i.i.d. loss.
- **Method:** `python3 experiments/runners/exp003_reliability.py experiments/configs/EXP-003_reliability.json`. Part A Monte Carlo (20 000 trials/point, Wilson 95 % CI, analytic i.i.d. reference); Part B real pipeline (AEAD records + receiver, 3000 messages, 4 cases); Part C byte overhead.
- **Seed:** 20261123 + point index (Part A); 20361123 + case index (Part B).
- **Result path:** `results/raw/EXP-003/run_20261123T170017Z/` (development run on uncommitted tree; frozen rerun in M7).
- **Outcome:** k = n Bernoulli 5 %: 0.774 (5/5) → 0.212 (30/30), matching (1−p)^n. Gilbert 5 %, burst 5: 0.909 → 0.702. Coded Bernoulli 10 %: 0.977–0.999; Gilbert 10 % burst 5: ≈0.85–0.91. Two-path: no benefit under burst. Abstraction check: 4/4 CIs overlap.
- **Interpretation:** Burst loss is less harmful than i.i.d. for k = n (contradicts manuscript). Erasure coding is necessary for availability. Label: SIMULATION RESULT.
- **Manuscript relevance:** R2 (DoS, erasure coding, multipath), manuscript Figs. 4–5 replaced.

## EXP-004 — Partial-capture plaintext recovery
- **Research question:** How much plaintext can an observer with exposed record keys recover from k−1 fragments, legacy XOR vs AONT+RS?
- **Hypothesis (pre-run):** legacy XOR leaks most bytes; AONT+RS recovery equals byte-guessing chance (1/256).
- **Method:** `python3 experiments/runners/exp004_partial_capture.py experiments/configs/EXP-004_partial_capture.json`; 2000 random 256-byte messages per configuration. Legacy: unmask all held fragments with the pad (N−1 of N held, pad included). AONT+RS: fill the missing shard with zeros, RS-decode, invert the AONT ignoring the integrity check.
- **Seed:** 4242.
- **Result path:** `results/raw/EXP-004/run_20261123T170052Z/`.
- **Outcome:** XOR 0.750 (N=5), 0.889, 0.947, 0.966 (N=30). AONT+RS mean 0.0039–0.0040, max 0.027.
- **Interpretation:** Confirms the construction change (DEC-008). This is an empirical check of one attack strategy, not a proof; the bound is in docs/fragmentation_aont.md. Label: SIMULATION RESULT.
- **Manuscript relevance:** R2 (AONT security), claim C5.
