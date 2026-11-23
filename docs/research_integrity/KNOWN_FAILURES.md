# Known Failures

Open and closed defects that affect research claims. Closed items stay listed
with the fixing commit and the test that guards them.

| ID | Found | Description | Evidence | Status |
|---|---|---|---|---|
| KF-001 | M1 | `tests/verify_v1.py`, `verify_v2.py`, `verify_final.py` fail (missing attributes/imports) | EXP-000 | OPEN (legacy; superseded by new test suite in M2+) |
| KF-002 | M1 | `SecureAgent.get_layer_key` calls `derive_single_key` with wrong arity → TypeError | EXP-000 | OPEN |
| KF-003 | M1 | `generate_validation.py` KeyError `'latency'` | EXP-000 | OPEN |
| KF-004 | M1 | XOR "AONT" leaks plaintext from strict subsets | EXP-001 probe 1 | OPEN → M3 |
| KF-005 | M1 | `aont_reconstruct` is order-dependent; empty fragments when len(M) < N−1 | EXP-001 probes 1c/1d | OPEN → M3 |
| KF-006 | M1 | `stochastic_loss.sh` labelled Markov but i.i.d. | EXP-001 probe 2 | OPEN → M3 |
| KF-007 | M1 | Wald CI in `monte_carlo_ci.sh` yields negative/zero-width intervals; unseeded | EXP-001 probe 3 | OPEN → M3 |
| KF-008 | M1 | CI workflow suppresses every failure (`|| true`, `|| echo`) | `.github/workflows/ci.yml` | OPEN → M7 |
| KF-009 | M1 | `protocol/secure_receive.py` raises undefined `SecurityError` | code inspection | OPEN (legacy path) |
| KF-010 | M1 | `network/traffic_shaper.py` interval depends on packet count (rate not constant) | code inspection | OPEN → M4 |
| KF-011 | M1 | `ARTIFACT_ENTRYPOINT.md` points to non-existent `Aegis-Grid-Unified/core/` | `ls` | OPEN → docs |
| KF-012 | M1 | θ = 0.35 in code vs 0.45 in manuscript | `agents/secure_agent.py` | OPEN → M5 |
