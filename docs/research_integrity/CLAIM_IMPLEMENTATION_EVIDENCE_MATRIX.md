# Claim–Implementation–Evidence Matrix

Living document. Each row is updated when a milestone changes its status; the
history is in git. Status vocabulary: VERIFIED · IMPLEMENTED — NOT FULLY TESTED ·
PARTIALLY IMPLEMENTED · SIMULATED · ANALYTICAL ONLY · PROPOSED · MISSING ·
INCONSISTENT · NOT REPRODUCIBLE.

Revision log of this file:
- **M1 baseline (2026-11-23)** — statuses below reflect `main@65f83bf`.
- **M2 (2026-11-23)** — rows for protocol, key establishment, encryption, authentication, replay, benchmarking updated in §A2.

## A. Research components (baseline, Milestone 1)

| Research component | Manuscript claim | Actual implementation (main@65f83bf) | Tests | Experimental evidence | Integrity status |
|---|---|---|---|---|---|
| Cryptographic protocol | ML-KEM + ML-DSA (FIPS 203/204), IND-CCA2 | AES-GCM helper class; RSA-2048 PKCS#1 v1.5 CA; no protocol state machine | none | none | MISSING |
| Key establishment | Session key from PQ KEM | none (random `master_key = os.urandom(32)` in `main.py`) | none | none | MISSING |
| Encryption | PQ encryption E_PQ | `AegisCrypt.seal` AES-GCM (random 16-B nonce from pycryptodome); unused by the experiment path | none | none | PARTIALLY IMPLEMENTED |
| Authentication | ML-DSA signing | RSA-2048 sign/verify of a challenge; `SignatureEngine` = SHA-256(key‖data) | none (legacy verify scripts fail) | none | INCONSISTENT |
| Replay protection | "Sequence number rejection" (Table 7) | none | none | none | MISSING |
| Fragmentation | AONT, negligible MI for strict subsets | XOR pad + pad-as-fragment | none | EXP-001: 88.4 % of plaintext recovered from a strict subset | INCONSISTENT |
| Reconstruction | All-or-nothing, order-independent | concatenation in received order | none | EXP-001: fails on reordered fragments | INCONSISTENT |
| Traffic shaping | Constant rate λ, padded sizes, dummies | sleep interval = window/len(packets); no size padding | none | none | PARTIALLY IMPLEMENTED |
| Traffic-analysis resistance | KS p>0.93, "indistinguishable" | none | none | no KS/classifier code in any branch | MISSING |
| Adaptive detection | CAP Eq. (14), θ | `cap = 0.85·cap + error`, θ=0.35 | none | none (Fig. 9 no source) | INCONSISTENT |
| Threshold selection | θ*=0.45 from sweep, FAR≈0 | constant 0.35 | none | none (Fig. 10 no source) | MISSING |
| Packet loss | Bernoulli + Gilbert–Elliott, 2000 MC | Bernoulli (unseeded); "GE" script is i.i.d. | none | EXP-001 probe 2/3 | INCONSISTENT |
| Cyber-physical model | Plant with safe set S_safe | none (`'execute' if status else 'drop'`; shell toy model in `v4/`) | none | none | MISSING |
| Safety constraints | X(t) ∈ S_safe | none | none | none | MISSING |
| Fallback control | U_safe applied when M̂=⊥ | binary drop | none | Fig. 11 hand-written CSV | MISSING |
| Benchmarking | O(N) timing <45 ms; PQ costs from ARM Cortex-M literature | none | none | none | MISSING |
| Baselines | TLS / IEC 62351 comparison tables | hand-assigned scores | none | none | ANALYTICAL ONLY (unsupported scores) |
| Statistical analysis | 95 % CI, KS | Wald CI (negative bounds), no KS | none | EXP-001 probe 3 | INCONSISTENT |
| Reproducibility | "All figures generated from simulation outputs" | most figures have no generator; no seeds | CI suppresses failures | EXP-000 | NOT REPRODUCIBLE |

## A2. Updates after Milestone 2 (branch `research-integrity-remediation`)

| Research component | New implementation | Tests | Evidence | Status |
|---|---|---|---|---|
| Cryptographic protocol | `aegis_pq/handshake.py`, `channel.py` (AGP/1, spec in `docs/protocol_specification.md`) | 46 security tests | EXP-002 | IMPLEMENTED — UNIT/SECURITY TESTED (not independently verified, no formal model) |
| Key establishment | ML-KEM-768/1024, optional X25519 hybrid, HKDF schedule | handshake agreement for 4 suites; invalid key; tampered ct | EXP-002 | IMPLEMENTED — TESTED |
| Encryption | AES-256-GCM record layer, TLS-1.3-style nonces | tamper, truncation, garbage, nonce-uniqueness | EXP-002 | IMPLEMENTED — TESTED |
| Authentication | ML-DSA-44/65/87 transcript signatures, X.509 pinned CA | wrong CA, expired, wrong peer, CA-as-EE, bad signatures, downgrade | EXP-002 | IMPLEMENTED — TESTED (no revocation) |
| Replay protection | per-epoch sliding window, deadline field | replay, reorder, too-old, late-then-replay | — | IMPLEMENTED — TESTED |
| Rekeying / expiry | HKDF key update, epoch grace=1, lifetime cap | rotation, old-epoch erasure, epoch skip, expiry | — | IMPLEMENTED — TESTED |
| Benchmarking | `experiments/runners/exp002_crypto_bench.py` | — | EXP-002 (x86-64 VM only) | HARDWARE MEASUREMENT (non-embedded) |

## B. Manuscript claim audit (baseline)

Location refers to `ieee paper3.docx` section headings (the manuscript has no
consistent section numbers — itself a defect).

| # | Manuscript claim | Location | Evidence required | Evidence available (M1) | Status | Required action |
|---|---|---|---|---|---|---|
| C1 | Integrates ML-KEM/ML-DSA (FIPS 203/204) | Abstract, §III L1 | Working implementation + measurements | none | MISSING | Implement and measure (M2) or remove |
| C2 | "All modelled properties are satisfied under sub-50 ms ... in simulations and emulations" | Abstract | Emulation runs | Emulation listed as *planned* in the same paper | INCONSISTENT | Remove "emulation" unless performed |
| C3 | Adaptive agents reduce worst-case latency to 35 ms (from 48 ms) | Abstract, §IV, Table 5, Conclusion | Latency measurement under load | constants in `gen_v3_latency_compare_csv.py` | NO MEASUREMENT | Replace with measured result (M5/M7) |
| C4 | GOOSE <4 ms motivation | §I | Evaluation at 3–4 ms | evaluation at 50 ms only | INCONSISTENT (Reviewer 2) | Scope traffic classes explicitly |
| C5 | XOR-based AONT; I(M;F′)≈0; "no extractable information" | §III L2, Fig. 6 | Construction + proof/bound | XOR transform leaks (EXP-001) | INCONSISTENT | Replace construction, state computational bound (M3) |
| C6 | Gu et al. [18] establish bounds | §III L2 | Correct citation | [18] is a COPA-DATA web page; Gu et al. is [24] | INCORRECT CITATION | Fix (M8) |
| C7 | KS p>0.93 ⇒ indistinguishable | §IV, Fig. 7, Table 4/5 | Test code + traces | none | NO SOURCE | Multivariate attacker on held-out traces (M4) |
| C8 | CAP crosses θ, θ*=0.45, FAR≈0, detection within 2 steps | §IV, Figs. 9–10 | Sweep code + data | none; θ=0.35 in code | NO SOURCE / INCONSISTENT | Formalise and evaluate vs EWMA/CUSUM (M5) |
| C9 | Fail-secure: X(t)∈S_safe, "no instance of unsafe actuation" | §IV, Fig. 11, Prop. 5 | Plant model, safe-set analysis | none | MISSING | Named power-system model (M6) |
| C10 | O(N) timing; T_total<45 ms; "proven 5 ms safety margin" | §IV Fig. 12, Conclusion | Timing measurements | none | NO SOURCE | Measure (M2/M7); remove "proven" |
| C11 | Markov burst-loss (Gilbert–Elliott) results | §IV Fig. 5 | GE implementation | i.i.d. implementation | INCONSISTENT | Implement GE (M3) |
| C12 | 2000 MC trials with 95 % CI | §IV Fig. 4 | Seeded runs, valid CI | unseeded; Wald CI with negative bounds | NOT REPRODUCIBLE | Wilson/Clopper–Pearson CI, seeds (M3) |
| C13 | PQ overhead "modelled from published Cortex-M benchmarks" | §II, §IV | Citation + values used | no citation, no values in code | MISSING | Measure on available hardware; cite external values only as labelled references |
| C14 | Baseline comparison (Tables 4, 6; Fig. 13) | §IV–V | Measured baselines at matched settings | hand-assigned scores | UNSUPPORTED | Implement TLS 1.3 / IEC 62351-style baselines (M7) |
| C15 | "traffic-indistinguishable communication without compromising real-time determinism" | Conclusion | — | — | OVERCLAIM | Rewrite (M8) |
| C16 | 2022 "Turkey blackout linked to a cyberattack" | §III L7 | Citation | none | UNCITED FACTUAL CLAIM | Verify or remove (M8) |
| C17 | Frontiers study [31] confirms exponential-decay temporal structure | §III L6 | Statement in source | not verified | UNVERIFIED | Verify or remove (M8) |
| C18 | Table 3 "Monte Carlo trials 2000", "Validity window 20–100 ms" | §IV Table 3 | Configs | partially (MC script only) | PARTIAL | Replace with config files |
| C19 | Sections numbered II..VII inconsistently; "VII. CONCLUSION" only numbered heading | whole paper | — | — | FORMAT DEFECT | Fix (M8) |
| C20 | Duplicate references [1]=[30], [13]=[20], [22]=[33] | References | — | — | FORMAT DEFECT | Fix (M8) |

## A3. Update after Milestone 3
| Claim | New status | Evidence |
|---|---|---|
| C5 (AONT, no information from partial sets) | REPLACED — package-transform AONT, computational bound, scoped to key-compromise; ANALYTICALLY DERIVED + SIMULATION RESULT | aegis_pq/aont.py, docs/fragmentation_aont.md, EXP-004 |
| C11 (Markov burst-loss results) | IMPLEMENTED (Gilbert–Elliott); manuscript conclusion contradicted (burst less harmful for k=n) | aegis_pq/netmodel.py, EXP-003 |
| C12 (MC with 95 % CI) | IMPLEMENTED — seeded, Wilson CI, validated against real pipeline | EXP-003 abstraction_check.json |
| Reconstruction / DoS (R2) | k-of-n Reed–Solomon added (scope addition, DEC-008) | aegis_pq/erasure.py, EXP-003 |

## Status after M4–M8 (2026-11-23)

| Claim | New status | Evidence |
|---|---|---|
| C1 ML-KEM/ML-DSA integration | IMPLEMENTED, TESTED, MEASURED (x86-64 VM) | aegis_pq/, tests/security, EXP-002, EXP-009 |
| C2 "simulations and emulations" | REMOVED — results labelled hardware measurement / simulation / analytical / assumption | manuscript §V-A |
| C3 latency 35 ms vs 48 ms | REMOVED — replaced by measured per-class latency | EXP-005 latency_delivery.csv |
| C4 GOOSE motivation vs 50 ms evaluation | SCOPED — Table 1 traffic classes; no protection-class suitability claim | manuscript §III-C |
| C5 AONT | REPLACED (see M3 table) | EXP-004, docs/fragmentation_aont.md |
| C6 Gu et al. citation | FIXED | manuscript references |
| C7 KS ⇒ indistinguishable | WITHDRAWN — multivariate attacker AUC 0.77–0.83 under shaping | EXP-006 (follow-up EXP-010/011) |
| C8 CAP θ*=0.45, FAR≈0 | WITHDRAWN — CAP = EWMA/(1−α); calibrated θ = 3.84; 1.75 false adaptations/1000 benign epochs; not better than CUSUM/EWMA | EXP-007, Proposition 2 (DEC-010, author decision: reframed as EWMA-based policy) |
| C9 fail-secure ⇒ safe set | QUALIFIED — plant study; safe hold time bounded (176.5 s at 0.1 pu/min); wind-up overshoot; stale-data case | EXP-008 (follow-up EXP-012) |
| C10 O(N) timing, "proven 5 ms margin" | REMOVED — measured handshake/record costs | EXP-002, EXP-009 |
| C11, C12 | IMPLEMENTED (see M3 table) | EXP-003 |
| C13 PQ costs from Cortex-M literature | REMOVED — own measurements; embedded not measured (BLOCKED) | EXP-002 |
| C14 baseline comparison | IMPLEMENTED — TLS 1.3 (PQ hybrid, PQ, classical; mutual), HMAC; chain-matched bytes | EXP-009, EXP-013 |
| C15 overclaims | REWRITTEN — manuscript Table 11 | manuscript |
| C16 2022 blackout claim | REMOVED (no verifiable source) | manuscript |
| C17 Frontiers [31] exponential decay | REMOVED; [31] cited only for HIL co-simulation | manuscript §II-E |
| C18 Table 3 parameters | REPLACED by config files | experiments/configs |
| C19, C20 numbering, duplicates | FIXED | manuscript build script (numbers by first citation; duplicates merged) |
