# Running Audit Log

Chronological, append-only.

- **2026-11-23 16:45 UTC — M1 start.** Branch `research-integrity-remediation` created from `65f83bf` (tag `paper-v1-final`). Working tree clean. Remote branches fetched (depth 1) for provenance search.
- **16:47 — EXP-000.** Legacy entry points executed; 6/8 fail. CI found to mask failures.
- **16:50 — Provenance search.** `git grep` across `main`, `paper-results-2026`, `audit-cleanup-2026`, `paper-2026-assets`, `BurhanAbdullah-patch-1` for ML-KEM/Kyber/Dilithium/KS/Kolmogorov/Gilbert/Markov/mutual-information code: none found.
- **16:52 — EXP-001.** Probes confirm XOR-transform leakage, i.i.d. "Markov" data, invalid CI, constant latency generator.
- **16:55 — Manuscript figures** extracted from the author's docx and matched to repository data (BASELINE_AUDIT §5).
- **M1 complete.** Deliverables: `BASELINE_AUDIT.md`, `CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md`, `DECISION_LOG.md` (DEC-001…004), `EXPERIMENT_REGISTER.md` (EXP-000/001), `KNOWN_FAILURES.md` (KF-001…012).
