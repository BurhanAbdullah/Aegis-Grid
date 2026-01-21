# Security Policy

## Scope and Intent

Aegis-Grid is a **research and experimental framework** for secure communication
in cyber-physical power systems. It is **not a consumer application**, **not an
authentication app**, and **not intended for end-user deployment**.

Security in this repository is defined in terms of **research correctness,
threat modeling, and reproducibility**, not operational uptime or patch SLAs.

---

## Supported Versions

Only the following versions are considered *actively supported for research use*:

| Version | Status | Notes |
|-------|--------|------|
| v5.x  | Conceptual | Quantum / unbounded adversary threat model (theoretical) |
| v4.x  | Supported | Agentic extensions and refinements |
| v3.3  | Frozen | Experimental artifact used in publications |
| < v3  | Unsupported | Archived or superseded |

The **v3.3 experimental release** is intentionally frozen and must not be
modified, to preserve reproducibility of published results.

---

## Security Model

Aegis-Grid does **not rely solely on cryptographic hardness assumptions**.
Instead, security is achieved through:

- Time-bounded validity
- Fail-secure semantics
- Fragmentation and all-or-nothing reconstruction
- Traffic indistinguishability
- Irreversible erasure after expiry

Later versions (v5+) explicitly consider **quantum-capable and unbounded
adversaries**.

---

## Reporting Vulnerabilities

This repository does **not** operate a bug bounty program.

If you identify:
- a flaw in the **threat model**
- an inconsistency in **security claims**
- an error affecting **experimental validity**

please open a **GitHub Issue** with:
- a clear description
- affected version(s)
- minimal reproduction steps (if applicable)

Do **not** report consumer-security issues, authentication bugs, or mobile app
vulnerabilities — they are out of scope.

---

## Disclosure Policy

Because this is research code:
- Responsible disclosure timelines are **best-effort**
- Fixes may take the form of **documentation updates**, not patches
- Some issues may be addressed in **future versions only**

---

## Non-Goals (Explicit)

Aegis-Grid does **not** claim:
- Production hardening
- Regulatory compliance
- Protection against physical-layer attacks
- Consumer-grade security guarantees

---

## Contact

For academic or research-related security discussions, use GitHub Issues.
Private contact may be requested only for coordinated research disclosure.

