# Legacy research states (v1–v5)

This directory holds the code, scripts, data and documents of the earlier
Aegis-Grid versions, moved here unchanged (with `git mv`, so their history is
kept) during the v6 revision. They are preserved for traceability of the earlier
manuscript and of the audit in `docs/research_integrity/BASELINE_AUDIT.md`, whose
paths refer to their original locations at `main@65f83bf`.

Nothing here is used to produce v6 results, with one exception: EXP-004 imports
`legacy/core/fragmentation.py` to measure the plaintext leakage of the legacy XOR
fragmentation that v6 replaces. Known defects of this code are listed in
`docs/research_integrity/KNOWN_FAILURES.md` (KF-001 to KF-012). The tests in
`legacy/tests/` are not part of the v6 test suite.
