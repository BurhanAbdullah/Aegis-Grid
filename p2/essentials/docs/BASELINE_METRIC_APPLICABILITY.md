Baseline Metric Applicability Clarification

This document explains why numerical simulation results are provided
only for Aegis-Grid and not for conventional security mechanisms.

Evaluated Metrics:
- Time-bounded message validity
- All-or-nothing fragment reconstruction
- Traffic indistinguishability (constant entropy)
- Fail-secure expiration semantics
- Cyber-physical actuation safety

System Applicability:

IEC 62351:
- Encryption-focused standard
- No time-bounded validity semantics
- No fragment-level reconstruction model
- No traffic shaping or entropy invariance
→ Metrics undefined, numerical simulation not meaningful

Encrypted-Only Communication:
- Provides confidentiality only
- Partial packet exposure possible
- Traffic patterns observable
→ Metrics undefined beyond encryption correctness

IDS-Based Adaptive Security:
- Detection-based, not fail-secure
- Acts after anomaly detection
- No correctness guarantees under delay or loss
→ Metrics incompatible with fail-secure evaluation

Aegis-Grid:
- Metrics explicitly defined by architecture
- Deterministic failure semantics
- Cyber-physical safety constraints enforced
→ Numerical simulation valid and provided

Conclusion:
Quantitative simulations are provided exclusively for Aegis-Grid
because the evaluated metrics are architectural properties,
not tunable performance parameters.
