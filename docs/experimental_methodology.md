# Experimental methodology (v6)

This document describes how every result of the v6 revision is produced. The
authoritative per-experiment record (question, pre-run hypothesis, seed, result
path, outcome) is `research_integrity/EXPERIMENT_REGISTER.md`; this file explains
the common rules and the design of each study.

## 1. Common rules

- **Registration before execution.** Each experiment has a register entry with its
  hypothesis written before the run. Follow-ups (EXP-010–013) were registered after
  an unfavourable result and before they were run; the original result is kept.
- **Provenance.** `experiments/common.py` creates `results/raw/<EXP>/run_<UTC>/` with
  `config.json`, `environment.json` (commit, dirty flag for tracked files, untracked
  files, interpreter, package and OpenSSL versions, CPU) and `status.json`
  (COMPLETED / FAILED, note; a note containing SUPERSEDED excludes the run from
  figures and manuscript numbers). Failed runs are never deleted.
- **No hand-typed numbers.** `scripts/paper_values.py` reads every manuscript number
  from the latest usable run into `results/paper_values.json`; figures are produced
  by `scripts/make_figures.py`, which writes the plotted data next to each figure
  and `figures/FIGURE_SOURCES.csv`.
- **Held-out evaluation.** Calibration/training data and test data are disjoint by
  session (EXP-006/011) or by seed range (EXP-007). Test data are used once.
- **Evidence labels.** HARDWARE MEASUREMENT (measured on the VM in
  `environment.json`), SIMULATION RESULT, ANALYTICALLY DERIVED, ASSUMPTION
  (modelling inputs; config keys carry the suffix `_ASSUMPTION`).
- **Platform.** One virtualised x86-64 VM (Intel Xeon 2.1 GHz, 4 vCPU), Python 3.13.
  No embedded device was measured. Network experiments use loopback sockets between
  processes; timing-sensitive runs (EXP-002, EXP-005/010, EXP-009, EXP-013) are run
  without other experiments in parallel.

## 2. Studies

| ID | Design | Statistics |
|---|---|---|
| EXP-002 | In-process timing of primitives (5000/1000 samples, 50 warm-up, GC off) and of 300 complete handshakes per suite | median, p95, p99 |
| EXP-003 | Monte Carlo delivery, 20 000 trials/point; Bernoulli and Gilbert–Elliott loss at equal mean; two-path; validation against the real pipeline (3000 messages, 4 cases) | Wilson 95 % CI; analytic (1−p)^n reference |
| EXP-004 | Adversary with record keys and all but one fragment; legacy XOR vs AONT+RS; 2000 × 256-byte messages | mean / max fraction of bytes recovered |
| EXP-005, EXP-010 | 40 sessions × 12 s per condition, randomised condition order, fresh handshake per session; UDP between processes; receiver timestamps (CLOCK_MONOTONIC); offline decode with the real receiver | delivery and latency per traffic class |
| EXP-006, EXP-011 | 36 window features; LR, k-NN, RF, HGB; sessions 0–23 train, 24–31 validation, 32–39 test | ROC-AUC with 2000-sample cluster bootstrap CI, 1000-permutation test, Hanley–McNeil minimum detectable AUC, Cliff's δ, KS (for comparison only) |
| EXP-007 | Epoch-level channel model; 6 attack families + benign congestion; thresholds calibrated on 50 benign sessions to 0.002 alarms/epoch; 30 test sessions per family; common random numbers; ablations | false adaptations / 1000 benign epochs, detection rate, delay, delivery |
| EXP-008, EXP-012 | ANDES 2.0.0 IEEE 14-bus `ieee14_full`, constant-power loads, AGC every 2 s through real AGP/1 objects; drop/delay/replay/forge; fail-secure vs insecure receiver | max deviation, first violation of ±0.2 Hz (SOGL Annex III, ASSUMPTION) |
| EXP-009 | Two processes over loopback: TLS 1.3 (forced and verified group; mutual and server-only), AGP/1, HMAC; 300 handshakes, 3000 × 96-byte messages | median, p99 |
| EXP-013 | In-memory TLS 1.3 mutual handshakes, default vs leaf-only chains | byte counts (deterministic), CPU median/p99 |

## 3. Known methodological weaknesses

See `limitations.md` and `research_integrity/KNOWN_FAILURES.md`. In particular:
the attacker knows the window alignment; the detector study is not packet-level;
the plant study covers one test system and controller.
