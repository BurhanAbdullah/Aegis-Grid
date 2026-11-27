# Security review register

This register separates implemented controls from assurance that remains open.
It is not a certification or a claim that the custom protocol is production
ready.

| ID | Area | Current control/evidence | Residual risk | Required action |
|---|---|---|---|---|
| SR-01 | AGP/1 custom handshake | ML-KEM, ML-DSA, transcript signatures, Finished MACs, suite tests | Purpose-built protocol has no independent formal analysis | Independent cryptographic review and formal model |
| SR-02 | Hybrid key schedule | ML-KEM and X25519 shared secrets concatenated before HKDF-Extract | Combiner argument and downgrade binding need expert review | Review combiner construction and transcript |
| SR-03 | Certificate lifecycle | Pinned CA, identity and validity checks | Revocation and automated rotation are absent | Define deployment PKI, revocation and rollover |
| SR-04 | Responder DoS | Parser and state-machine checks | No stateless cookie or pre-authentication rate limit; responder performs KEM/signature work | Add deployment rate limits/cookie before production |
| SR-05 | Record nonce management | Per-epoch sequence-derived nonce, rekeying, tests | Correctness depends on persistent single-writer session state | Document process restart and state-loss rules |
| SR-06 | Replay protection | Authenticated sequence window per epoch | Application-level duplicate message semantics also require bounded ID history | Keep fail-closed delivered history; rotate sessions at capacity |
| SR-07 | Message reassembly | v6.1 candidate bounds pending count and memory; validates metadata and shard lengths | Defaults are research values; timer integration is host responsibility | Size limits from deployment workload; schedule expire_due() |
| SR-08 | Fragment wire format | v6.1 candidate constrains n to 255 due u8 field | Wire version has no negotiation for future larger counts | Preserve constraint or define a versioned format |
| SR-09 | AONT security | Transform implementation and EXP-004 attack experiment | General proof sketch is incomplete; one attack strategy is not a proof | Keep theorem withdrawn; obtain independent proof review |
| SR-10 | AEAD and PQ primitives | Uses maintained cryptography library primitives | Library security and implementation side channels are trusted, not audited here | Track upstream advisories and pin reviewed versions |
| SR-11 | Time/deadline | Authenticated generation time/deadline and configured clock skew | Clock synchronisation attacks are out of scope | Specify PTP/GNSS trust and monitoring |
| SR-12 | Traffic analysis | Loopback traces and held-out classifiers | Finite attacker models/sample sizes; no indistinguishability proof | State measured AUC and uncertainty only |
| SR-13 | Physical fail-safe | IEEE 14-bus AGC simulation with hold-last-valid fallback | One model and operating envelope; no formal invariant proof | Validate against multiple plants and controller constraints |
| SR-14 | Supply-chain and release | Pinned requirements and CI workflow | No SBOM/signature policy or dependency vulnerability gate | Add SBOM and dependency review before production |
| SR-15 | Licensing | Restrictive academic-use licence is committed | Public availability is not permission to redistribute | Author must select and approve licence |

## Reporting

Do not publish operational secrets, private keys, certificates from a real
deployment, or exploitable details of a live grid installation. Report security
issues privately to the repository owner with a reproducible test case and
affected commit. This research artefact is not approved for direct deployment
in operational technology without independent review and a deployment safety
case.
