# Aegis-Grid v6 architecture (as implemented)

Every component below exists in `aegis_pq/` and is covered by tests. Components
from the original manuscript that are not implemented are listed at the end.

```
 sender (control centre / gateway)                                receiver (RTU / plant / relay gateway)
 ┌───────────────────────────────────────────┐                   ┌───────────────────────────────────────────┐
 │ application message M, deadline D         │                   │ U = M̂ if valid, else U_safe (L7)          │
 │ L2  package-transform AONT  Y = AONT(M)   │                   │ L2  AONT⁻¹ (integrity canary)             │
 │ L2  RS(k,n) erasure code  → n shards      │                   │ L2  RS decode from any k shards           │
 │ L1  AGP/1 record: AES-256-GCM, epoch,     │   UDP / IP        │ L1/L5 open record: AEAD, session, epoch,  │
 │     seq, t_gen, deadline (authenticated)  │ ───────────────▶  │     replay window, deadline + skew        │
 │ L3/L4 fixed-size records, constant rate Δ,│  (observable by   │ L6  observables → CAP / policy            │
 │     encrypted dummies, EDF queue          │   the adversary)  │                                           │
 │ L6  bounded adaptation of n (k fixed)     │                   │                                           │
 └───────────────────────────────────────────┘                   └───────────────────────────────────────────┘
          ▲  AGP/1 handshake (ML-KEM-768/1024 ± X25519, ML-DSA-44/65/87, X.509 with pinned grid CA)  ▲
```

| Layer | Function | Module | Evidence |
|---|---|---|---|
| L1 | Authenticated PQ key establishment; AEAD record layer | `handshake.py`, `channel.py`, `pki.py`, `suites.py` | tests/security (46), EXP-002, EXP-009 |
| L2 | Package-transform AONT + RS(k,n) | `aont.py`, `erasure.py`, `pipeline.py` | tests/unit, EXP-003, EXP-004 |
| L3–L4 | Fixed-size records, constant-rate emission, dummies, EDF, late-drop | `shaping.py` | tests/unit/test_shaping.py, EXP-005/006 |
| L5 | Authenticated deadline; replay window; session lifetime | `channel.py` | tests/security |
| L6 | CAP (EWMA-type statistic) + hysteretic two-level policy | `detectors.py` | tests/unit/test_detectors.py, EXP-007 |
| L7 | Fail-secure fallback (hold last validated set-point) | `experiments/runners/exp008_cyberphysical_agc.py` | EXP-008 (IEEE 14-bus) |

## Changes with respect to the original manuscript
| Original | Now | Reason |
|---|---|---|
| "PQ encryption" modelled by AES-GCM proxy + Cortex-M literature values | Implemented ML-KEM/ML-DSA handshake; costs measured on x86-64 VM only | R2, DEC-005/007 |
| XOR "AONT", all N fragments required | Package-transform AONT (computational) + RS(k,n); k=n reproduces the original | R2, DEC-008 |
| Size perturbation + time-keyed permutation (Eq. 7–9) | Fixed size, fixed rate, encrypted dummies; no permutation (not needed under per-record AEAD) | simplicity; measured in EXP-006 |
| CAP adjusts N, ρ, λ (reducing N weakens L2) | CAP is shown equal to an EWMA chart; policy only raises n, never lowers k | R2, EXP-007 |
| U_safe abstract | Hold-last-validated set-point on an AGC loop of the IEEE 14-bus case | R2, EXP-008 |

## Not implemented
- Embedded/RTU deployment and hardware PQC acceleration.
- Model checking of the adaptive policy.
- Multicast GOOSE/SV transport (AGP/1 is unicast over UDP).
