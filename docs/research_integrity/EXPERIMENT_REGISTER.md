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

## EXP-005 — UDP-loopback traffic traces under four protection conditions
- **Research question:** What does a passive on-path observer see (arrival time, datagram size) when AGP/1 carries a grid workload unshaped, size-padded, or shaped at a constant rate (Δ = 2 ms, 1 ms)? What latency and delivery does each condition give?
- **Hypothesis (pre-run):** Unshaped and padded traffic reveal activity through counts/timing; constant-rate shaping hides counts but adds queueing delay of order Δ·(queue length) and may miss the 20 ms event deadline at Δ = 2 ms.
- **Method:** `python3 experiments/runners/exp005_traffic_capture.py` (config `EXP-005_traffic_capture.json`). 40 sessions × 12 s × 4 conditions (order randomised per session); fresh AGP/1 handshake per session/condition; sender and receiver in separate processes; receiver timestamps with CLOCK_MONOTONIC; offline decryption/reassembly with the real Receiver. Workload (ASSUMPTION): 25 frames/s telemetry in every 250 ms window plus, per window, nothing (steady), a 7-message event burst (GOOSE-like doubling retransmission) or a 2-message command; RS(5,7).
- **Seed:** 5005. **Environment:** environment.json (commit bda49aa parent tree, clean).
- **Result path:** `results/raw/EXP-005/run_20261123T170717Z/` (traces.csv.gz, messages.csv.gz, window_labels.csv, session_summary.json).
- **Outcome:** see EXP-006 for the attacker. Latency/delivery (EXP-006 latency_delivery.csv): unshaped/padded p50 ≈ 0.6–0.8 ms, all classes delivered; shaped 1 ms: event p99 18.1 ms, delivery 0.999; shaped 2 ms: event delivery **0.432** (late fragments dropped by the shaper), telemetry p99 58 ms; bandwidth ×2.13 (2 ms) and ×4.27 (1 ms) relative to unshaped.
- **Label:** HARDWARE MEASUREMENT (VM loopback).

## EXP-006 — Multivariate traffic-analysis attacker on EXP-005 traces
- **Research question:** Can a passive attacker tell steady windows from active (event/command) windows, per condition?
- **Hypothesis (pre-run):** AUC ≈ 1 unshaped/padded; near 0.5 under constant-rate shaping.
- **Method:** `exp006_traffic_attacker.py`; 36 per-window features (counts, sizes, IAT quantiles, sub-window counts, log-IAT histogram); logistic regression, k-NN, random forest, histogram gradient boosting; sessions 0–23 train, 24–31 validation (hyper-parameter choice), 32–39 test (used once); cluster bootstrap over test sessions (2000); permutation test (1000); minimum detectable AUC; Cliff's δ; KS tests for comparison with the manuscript's method.
- **Seed:** 6006. **Result path:** `results/raw/EXP-006/run_20261123T182614Z/`. environment.json shows `git_dirty: true` only because an untracked EXP-009 result directory existed; code = commit f5cd291.
- **Outcome:** unshaped and padded: AUC 1.000 for every model. **Shaped 2 ms: binary AUC 0.77–0.82 (best RF 0.821, CI 0.765–0.863); shaped 1 ms: 0.81–0.83; permutation p = 0.001.** The hypothesis is rejected for shaping. KS on per-window packet count gives p = 1.0 (shaped), i.e. a KS test reports "no difference" while the classifier separates the classes. Largest effect sizes: IAT p10/p90 (|δ| ≈ 0.42 at 2 ms), i.e. emission-timing jitter.
- **Interpretation:** constant-rate emission as implemented in Python leaks activity through timing jitter (an implementation timing side channel). The manuscript's KS-based indistinguishability claim is not supported. Label: SIMULATION RESULT on HARDWARE-MEASURED traces.
- **Manuscript relevance:** R2 (KS ≠ indistinguishability, multivariate attacker, effect sizes, power, overhead); R1 (timing side channels).

## EXP-007 — CAP vs change-detection baselines
- **Research question:** Does CAP detect attack pressure faster or with fewer false adaptations than Shewhart, EWMA and CUSUM, and does the bounded adaptation help delivery?
- **Hypothesis (pre-run):** CAP behaves like EWMA (they are algebraically related); no detector dominates; adaptation improves delivery relative to static n = 7 at a bandwidth cost.
- **Method:** `exp007_cap_detection.py`; epoch-level channel model; thresholds calibrated on 50 benign sessions only to an alarm fraction of 0.002; 6 attack families + benign-with-congestion test sessions (30 each), never used for calibration; common random numbers; shared policy (n 7→10, hold 8 epochs).
- **Seed:** calibration 70000+, test 80000+. **Result path:** `results/raw/EXP-007/run_20261123T182604Z/`.
- **Outcome:** all adaptive detectors detect all six families (detection 1.0) — the families are too strong to separate detectors on detection rate. False adaptations per 1000 benign epochs: CUSUM 0.35, Shewhart 0.97, CAP 1.75, EWMA 2.98. Slow-ramp mean delay (epochs): EWMA 13.3, CAP 14.0, Shewhart 18.4, CUSUM 20.6. Every detector alarmed in every benign congestion episode. Delivery under delay injection: adaptive 0.97–0.98 vs static n=7 0.776 vs static n=10 0.983. CAP with α = 0 equals Shewhart exactly (sanity check). Shewhart could only be calibrated to 0.0005 (discrete score), so its comparison is not perfectly matched. Loss-only CAP misses delay injection (0.07) and injection floods (0.10).
- **Interpretation:** CAP is an EWMA-type chart; it is not superior to CUSUM or EWMA; the value lies in the multi-observable score and the bounded policy. Label: SIMULATION RESULT.
- **Manuscript relevance:** R2 (formal CAP, baselines, held-out attacks, ablation); claims C9/C10 (θ = 0.45, "false adaptation ≈ 0") replaced.

## EXP-008 — Fail-secure AGC on the IEEE 14-bus dynamic case
- **Research question:** What happens to system frequency when AGC set-points over AGP/1 are dropped, delayed, replayed or forged, with U_safe = hold last validated set-point, compared with an unauthenticated receiver? How long can U_safe be held during a load ramp?
- **Hypothesis (pre-run):** forged commands drive the insecure receiver outside the band while AGP/1 rejects them; under drop, both receivers hold and the band is crossed after ≈ (band/f0)·Σ(1/R)/r ≈ 200 s at r = 0.1 pu/min.
- **Method:** `exp008_cyberphysical_agc.py`; Andes 2.0.0 `ieee14_full` (5 GENROU, 5 TGOV1, EXST1/ESST3A), constant-power loads, AGC every 2 s, commands sealed/opened by real AGP/1 objects with simulation-synchronised clocks.
- **Result path:** `results/raw/EXP-008/run_20261123T182611Z/`.
- **Outcome:** forge: insecure −0.55 Hz / +1.21 Hz excursion, outside the ±0.2 Hz band 2.5 s after attack start; AGP/1 rejected all forged records (150 AUTH_FAIL, 150 BAD_VERSION) and stayed within 0.082 Hz. Drop, held set-points: during a 120 s outage the band was not crossed (it was crossed 2.5 s *after* delivery resumed, by the wind-up overshoot below); during a 240 s outage the under-frequency band was crossed 176.5 s after the attack started (analytic estimate 200 s, which ignores AGC lag before the attack); at 0.2 pu/min after 78.5 s (analytic 100 s); at 0.05 pu/min the 242.5 s crossing is again the post-recovery overshoot (analytic hold limit 400 s exceeds the outage). **On recovery after a 240 s outage the accumulated AGC integral caused a +1.15 Hz overshoot** (integrator wind-up at the control centre) — fail-secure at the receiver alone does not prevent this. Delay (10 s stale): the insecure receiver that applied stale commands had a *smaller* deviation (0.031 Hz) than the fail-secure hold (0.082 Hz) — rejecting stale data is not always better for frequency, it is a safety policy. Replay: insecure 0.101 Hz vs 0.082 Hz.
- **Label:** SIMULATION RESULT (plant model) with real protocol objects. Limits are ASSUMPTIONS (SOGL Annex III values applied to a 60 Hz test case).
