# Baseline comparison

Baselines are implemented in `baselines/` and evaluated at matched settings.

| Baseline | Implementation | Matched setting | Experiment |
|---|---|---|---|
| TLS 1.3, X25519MLKEM768 / MLKEM768 / X25519 | Python `ssl` (OpenSSL 3.5), `baselines/tls13.py` | ML-DSA-65 (PQ) or ECDSA P-256 (classical) certificates; mutual authentication (AGP/1 always authenticates both sides); no session tickets; 1-byte ack after the handshake; group verified from the ServerHello | EXP-009 |
| TLS 1.3, leaf-only chains | as above with partial-chain trust of the peer's end-entity certificate | same certificate count as AGP/1 (OpenSSL otherwise adds the CA certificate to each chain) — byte/CPU comparison only, not a deployable trust model | EXP-013 |
| IEC 62351-6-style HMAC | `baselines/iec62351_hmac.py` | HMAC-SHA256/128, sequence number, timestamp, age check; pre-shared key; no confidentiality | EXP-009 |
| Shewhart, EWMA (λ = 0.2), CUSUM (κ = 0.5) | `aegis_pq/detectors.py` | same normalised observables, same policy, thresholds calibrated on the same benign data to the same alarm fraction | EXP-007 |
| Static n = 7, n = 10 | `AdaptationPolicy` with `Never` detector | same k and record size | EXP-007 |
| Insecure accept-all receiver | `exp008_cyberphysical_agc.py` | same plant, ramp and attacks | EXP-008 |
| Legacy XOR fragmentation | `legacy/core/` (kept only for this comparison) | same message sizes and fragment counts | EXP-004 |
| Unshaped / padded traffic | `exp005_traffic_capture.py` | same workload, sessions and codes | EXP-005/006 |

## Main findings (from the registered runs)
- AGP/1 handshake ≈1.2× the wall time of mutual TLS 1.3 with the same primitives;
  bytes equal within a few percent once certificate chains are matched (EXP-013).
- AGP/1 per-message latency ≈2× TLS on loopback (Python record path; RS(5,7) ≈4×).
- CAP is not better than CUSUM (false adaptations) or EWMA (ramp delay).
- Fail-secure rejects forged/replayed commands that move an insecure receiver
  outside the frequency band; under a pure delay attack applying stale commands
  gave a smaller deviation.
