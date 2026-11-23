# Decision Log

Every material research decision is recorded here before or when it is made.
Entries are append-only; superseded decisions are marked, not deleted.

---

## DEC-001 — Work on a dedicated branch; preserve all legacy artefacts
- **Date:** 2026-11-23
- **Issue:** Remediation must not overwrite the submitted research state.
- **Previous approach:** Direct commits to `main`; force-updated tags (see `TAG_NOTES.md`).
- **Decision:** All work on `research-integrity-remediation` from `65f83bf` (tag `paper-v1-final`). No force-push, no history rewrite, no deletion of legacy CSVs/figures/scripts. New code and results live in new paths. No merge to `main` without the author's explicit approval.
- **Scientific impact:** Legacy results remain inspectable for provenance.
- **Verification:** `git log main..research-integrity-remediation`.

## DEC-002 — Manuscript source of record and non-publication
- **Date:** 2026-11-23
- **Issue:** The file supplied as "manuscript.docx" is Reviewer 1's report, not the manuscript. The repository is public.
- **Decision:** Audit against the author's `ieee paper3.docx` (SHA-256 `9c757ef5…7066112`), which matches every passage Reviewer 2 quotes. Do not commit the manuscript or reviewer reports to the public repository; reference reviewer concerns by ID (R1.x, R2.x) with short paraphrases only.
- **Assumption:** The IJIS PDF is textually equivalent to this file. To be re-checked if the author supplies the submitted PDF.

## DEC-003 — Legacy figures are not evidence
- **Date:** 2026-11-23
- **Issue:** Figs. 6–13 and headline numbers (48/35 ms, KS p>0.93, θ*=0.45, <45 ms) have no generating code or are produced from typed constants (BASELINE_AUDIT §5).
- **Decision:** None of these values will be reused. Every number in the revised manuscript must come from a registered experiment in `EXPERIMENT_REGISTER.md` with raw output under `results/raw/`.
- **Manuscript impact:** All quantitative results will change. Reviewer concern addressed: R2 (evaluation, reproducibility), R1 (empirical PQC benchmarks).

## DEC-004 — Remediation scope follows the reviewer concerns; central hypothesis retained pending evidence
- **Date:** 2026-11-23
- **Issue:** Rule 4 forbids silent scope changes.
- **Decision:** The central question is kept: *can a smart-grid message path combine PQ key establishment, fragment-level all-or-nothing reconstruction, constant-rate cover traffic, deadline enforcement and fail-secure fallback within the latency budget of a stated traffic class?* What changes is the evidence standard. If experiments show a component is not viable (e.g. shaping does not resist a classifier, or the pipeline cannot meet a class deadline), the claim is narrowed and the change is logged here rather than tuned away.
- **Stop-and-ask trigger:** Removing a major contribution (e.g. AONT layer or CAP agent) or replacing the hypothesis requires the author's decision.

## DEC-005 — Replace proxy crypto with a complete AGP/1 protocol built on standard primitives
- **Date:** 2026-11-23
- **Issue:** R2 (protocol completeness), R1 (parameter sets, negotiation, native vs hybrid, handshake cost). No PQ code existed (BASELINE_AUDIT §3).
- **Alternatives:** (a) narrow the paper to "AES-GCM with assumed PQ key exchange"; (b) use TLS 1.3 with hybrid groups only; (c) implement a purpose-built handshake on library primitives.
- **Decision:** (c) for the proposed architecture, using `cryptography` 50.0.1 (OpenSSL 3.5 backend) for ML-KEM, ML-DSA, X25519, AES-GCM, HKDF, X.509 — no primitive implemented from scratch. TLS 1.3 is used as a **baseline** (Milestone 7), not discarded.
- **Scientific impact:** PQ costs become measurements of this implementation instead of imported literature values. A custom handshake has not had the scrutiny TLS 1.3 has; this is stated as a limitation and the paper must not claim the protocol is proven secure.
- **Verification:** 46 security tests (`tests/security/test_protocol.py`); mutation smoke check (disabling replay, deadline or CA-signature checks makes ≥1 test fail).

## DEC-006 — ML-KEM-512 not offered
- **Date:** 2026-11-23
- **Issue:** R1 asks which ML-KEM parameter set is used.
- **Evidence:** `cryptography.hazmat.primitives.asymmetric.mlkem` exposes only `MLKEM768*` and `MLKEM1024*` classes in v50.0.1.
- **Decision:** Offer ML-KEM-768 (category 3, default) and ML-KEM-1024 (category 5). ML-KEM-512 results are reported as NOT YET EXPERIMENTALLY VERIFIED.

## DEC-007 — Benchmark scope and labelling
- **Date:** 2026-11-23
- **Decision:** All timing numbers are HARDWARE MEASUREMENTS on a virtualised x86-64 VM (EXP-002). They are not presented as embedded/RTU/Cortex-M results. If published embedded benchmarks are cited, they are labelled "external reference value" with source.
