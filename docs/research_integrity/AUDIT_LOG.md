# Running Audit Log

Chronological, append-only.

- **2026-11-23 16:45 UTC — M1 start.** Branch `research-integrity-remediation` created from `65f83bf` (tag `paper-v1-final`). Working tree clean. Remote branches fetched (depth 1) for provenance search.
- **16:47 — EXP-000.** Legacy entry points executed; 6/8 fail. CI found to mask failures.
- **16:50 — Provenance search.** `git grep` across `main`, `paper-results-2026`, `audit-cleanup-2026`, `paper-2026-assets`, `BurhanAbdullah-patch-1` for ML-KEM/Kyber/Dilithium/KS/Kolmogorov/Gilbert/Markov/mutual-information code: none found.
- **16:52 — EXP-001.** Probes confirm XOR-transform leakage, i.i.d. "Markov" data, invalid CI, constant latency generator.
- **16:55 — Manuscript figures** extracted from the author's docx and matched to repository data (BASELINE_AUDIT §5).
- **M1 complete.** Deliverables: `BASELINE_AUDIT.md`, `CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md`, `DECISION_LOG.md` (DEC-001…004), `EXPERIMENT_REGISTER.md` (EXP-000/001), `KNOWN_FAILURES.md` (KF-001…012).
- **17:05 — M2.** AGP/1 implemented (aegis_pq/), 46 security tests pass, mutation smoke detects disabled replay/deadline/CA checks; EXP-002 dev benchmark run.
- **17:20 — M3.** Package-transform AONT + RS(k,n) + Gilbert–Elliott implemented; EXP-003/004 run; DEC-008; KF-004…007 fixed, KF-013/014 opened.
- **17:07 — M4.** Constant-rate shaper and UDP trace capture (EXP-005) implemented; KF-010 superseded.
- **18:22–18:47 — M4–M7.** CAP and CUSUM/EWMA/Shewhart detectors, TLS 1.3 and HMAC baselines, IEEE 14-bus AGC study. EXP-006 (attacker: leak under shaping, KF-015), EXP-007 (CAP not better than CUSUM/EWMA, KF-017), EXP-008 (hold time and wind-up, KF-018), EXP-009 (protocol baselines). Server-auth-only TLS run kept; matched mutual-auth run added (DEC-009…012).
- **18:58 — Chain mismatch found** in mutual TLS (CA certificate auto-chained); EXP-013 registered (DEC-013). Follow-ups EXP-010/011/012 registered before running.
- **19:02 — Correction.** `cryptography` backend is OpenSSL 4.0.2, not 3.5 (KF-021).
- **19:31 — EXP-011 crashed** (no unshaped condition in its input); failed run kept, runner fixed (d74c690), rerun gave the registered result (KF-022).
- **19:35 — Results.** EXP-010…013 and frozen clean-tree reruns of EXP-002/003/004 committed; outcomes registered (DEC-014).
- **19:38 — M8.** Figures regenerated at 600 dpi; `check_manuscript_numbers.py` reproduces all manuscript values from `results/raw`. Manuscript and response letter rebuilt from `results/paper_values.json` outside the repository (not committed).
- **M9 — Repository cleanup (DEC-015).** v1–v5 code, scripts, data and documents moved unchanged to `legacy/` with `git mv`; README, ARTIFACT_ENTRYPOINT (KF-011), `pyproject.toml`, CI that fails on failure (KF-008); smoke configurations for every runner. Final `verify_all.sh --smoke` recorded in `FINAL_VALIDATION_REPORT.md`.
