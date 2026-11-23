# Known Failures

Open and closed defects that affect research claims. Closed items stay listed
with the fixing commit and the test that guards them.

| ID | Found | Description | Evidence | Status |
|---|---|---|---|---|
| KF-001 | M1 | `tests/verify_v1.py`, `verify_v2.py`, `verify_final.py` fail (missing attributes/imports) | EXP-000 | OPEN (legacy; superseded by new test suite in M2+) |
| KF-002 | M1 | `SecureAgent.get_layer_key` calls `derive_single_key` with wrong arity → TypeError | EXP-000 | OPEN |
| KF-003 | M1 | `generate_validation.py` KeyError `'latency'` | EXP-000 | OPEN |
| KF-004 | M1 | XOR "AONT" leaks plaintext from strict subsets | EXP-001 probe 1 | FIXED in M3 (DEC-008, EXP-004); legacy kept for comparison |
| KF-005 | M1 | `aont_reconstruct` is order-dependent; empty fragments when len(M) < N−1 | EXP-001 probes 1c/1d | FIXED in M3 (indexed shards, tests/integration/test_pipeline.py) |
| KF-006 | M1 | `stochastic_loss.sh` labelled Markov but i.i.d. | EXP-001 probe 2 | FIXED in M3 (aegis_pq/netmodel.py Gilbert–Elliott, EXP-003) |
| KF-007 | M1 | Wald CI in `monte_carlo_ci.sh` yields negative/zero-width intervals; unseeded | EXP-001 probe 3 | FIXED in M3 (Wilson CI, seeded, EXP-003) |
| KF-008 | M1 | CI workflow suppresses every failure (`|| true`, `|| echo`) | `.github/workflows/ci.yml` | OPEN → M7 |
| KF-009 | M1 | `protocol/secure_receive.py` raises undefined `SecurityError` | code inspection | OPEN (legacy path) |
| KF-010 | M1 | `network/traffic_shaper.py` interval depends on packet count (rate not constant) | code inspection | OPEN → M4 |
| KF-011 | M1 | `ARTIFACT_ENTRYPOINT.md` points to non-existent `Aegis-Grid-Unified/core/` | `ls` | OPEN → docs |
| KF-012 | M1 | θ = 0.35 in code vs 0.45 in manuscript | `agents/secure_agent.py` | OPEN → M5 |
| KF-013 | M3 | AONT bound weak for short shards (32 B message, k=20 ⇒ 40 unknown bits) | docs/fragmentation_aont.md §3 | OPEN — limitation, reported |
| KF-014 | M3 | Erasure coding only partly restores delivery under bursts (≈0.85–0.91 at 10 %, burst 5); two-path no benefit | EXP-003 | OPEN — reported as result |
| KF-015 | M4 | Constant-rate shaping leaks activity via emission-timing jitter (AUC 0.79–0.83) | EXP-006 | OPEN — follow-up EXP-010/011 |
| KF-016 | M4 | Shaping at Δ = 2 ms delivers only 43 % of 20 ms-deadline event messages | EXP-005/006 | OPEN — reported; Δ = 1 ms meets it at ×4.3 bandwidth |
| KF-017 | M5 | Every detector raises false adaptations in benign congestion episodes | EXP-007 | OPEN — reported |
| KF-018 | M6 | AGC integrator wind-up causes +1.15 Hz overshoot after a 240 s command outage | EXP-008 | OPEN — follow-up EXP-012 |
| KF-019 | M7 | AGP/1 handshake (≈5 ms, 20 kB) is slower and larger than TLS 1.3 with ML-KEM/ML-DSA (≈2.6 ms server-auth); per-message latency ≈2× TLS (Python record/AONT path) | EXP-009 | OPEN — reported |
| KF-020 | M1–M7 | EXP-006/007/008 environment.json shows git_dirty=true caused only by an untracked result directory (provenance logic since fixed to separate untracked files) | environment.json | DOCUMENTED |
