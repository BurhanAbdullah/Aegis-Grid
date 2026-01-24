# Aegis-Grid — Model Comparison (No Plots)

This document compares all Aegis-Grid versions purely at the **model level**.

No plots, fitted curves, or visual results are used.
All statements map directly to repository structure, code, or documented logic.

---

## Version Comparison

| Version | Model Type | Core Mechanism | Threat Model | Cryptographic Assumption | Agent Role | Fail-Secure Meaning |
|--------|-----------|---------------|--------------|--------------------------|------------|--------------------|
| v1 | Deterministic protocol | Fragmentation + all-or-nothing reconstruction | Passive eavesdropper, packet loss | Classical symmetric cryptography | None | Incomplete messages are unrecoverable |
| v2 | Adaptive stochastic model | Adaptive (n,k) thresholding + attack pressure | Sustained loss, active degradation | Classical crypto + probabilistic loss | Reactive | Messages invalidated under attack |
| v2_model | Analytical abstraction | State-space / stochastic vectors | Abstract adversary | None (symbolic model) | None | Formal fail-secure state |
| v3 | Agentic control system | Closed-loop security adaptation | Adaptive adversary | Crypto + control stability | Autonomous | Agent refuses unsafe delivery |
| v3.3 | Cyber-physical experiment | v3 + grid timing constraints | Timing + loss + CPS delay | Same as v3 | Same as v3 | Safety over availability |
| v4 | Cyber-physical model | Grid-aware timing invariants | Cyber + physical attacker | Crypto + physical bounds | Safety-constrained | Security cannot violate grid safety |
| v5 | Conceptual threat model | Information-theoretic invalidation | Quantum + infinite compute | None | Policy-level | Message is useless by design |

---

## Important Clarifications

- No version claims unbreakable encryption
- No quantum resistance is claimed as an implementation
- v5 is a **conceptual limit model**, not deployed code
- All versions enforce **fail-secure**, not fail-open behavior

---

## Verification

Reviewers can verify claims by inspecting:
- Version folders (`/v1` … `/v5`)
- `SECURITY.md`
- Tagged releases
- Protocol logic under `/protocol`, `/core`, `/agents`

No empirical plots are required to validate these models.
