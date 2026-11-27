# Decision Log

Every material research decision is recorded here before or when it is made.
Entries are append-only; superseded decisions are marked, not deleted.

---

## DEC-001 — Work on a dedicated branch; preserve all legacy artefacts
- **Date:** 2026-11-23
- **Issue:** Remediation must not overwrite the submitted research state.
- **Previous approach:** Direct commits to `main`; force-updated tags (see `TAG_NOTES.md`).
- **Decision:** All work on `research-integrity-remediation` from `65f83bf` (tag `paper-v1-final`). No force-push, no history rewrite, no deletion of legacy CSVs/figures/scripts. New code and results live in new paths. No merge to `main` without the author's explicit approval.
- **Scientific impact:** Legacy results remain inspectable for provenance.
- **Verification:** `git log main..research-integrity-remediation`.

## DEC-002 — Manuscript source of record and non-publication
- **Date:** 2026-11-23
- **Issue:** The file supplied as "manuscript.docx" is Reviewer 1's report, not the manuscript. The repository is public.
- **Decision:** Audit against the author's `ieee paper3.docx` (SHA-256 `9c757ef5…7066112`), which matches every passage Reviewer 2 quotes. Do not commit the manuscript or reviewer reports to the public repository; reference reviewer concerns by ID (R1.x, R2.x) with short paraphrases only.
- **Assumption:** The IJIS PDF is textually equivalent to this file. To be re-checked if the author supplies the submitted PDF.

## DEC-003 — Legacy figures are not evidence
- **Date:** 2026-11-23
- **Issue:** Figs. 6–13 and headline numbers (48/35 ms, KS p>0.93, θ*=0.45, <45 ms) have no generating code or are produced from typed constants (BASELINE_AUDIT §5).
- **Decision:** None of these values will be reused. Every number in the revised manuscript must come from a registered experiment in `EXPERIMENT_REGISTER.md` with raw output under `results/raw/`.
- **Manuscript impact:** All quantitative results will change. Reviewer concern addressed: R2 (evaluation, reproducibility), R1 (empirical PQC benchmarks).

## DEC-004 — Remediation scope follows the reviewer concerns; central hypothesis retained pending evidence
- **Date:** 2026-11-23
- **Issue:** Rule 4 forbids silent scope changes.
- **Decision:** The central question is kept: *can a smart-grid message path combine PQ key establishment, fragment-level all-or-nothing reconstruction, constant-rate cover traffic, deadline enforcement and fail-secure fallback within the latency budget of a stated traffic class?* What changes is the evidence standard. If experiments show a component is not viable (e.g. shaping does not resist a classifier, or the pipeline cannot meet a class deadline), the claim is narrowed and the change is logged here rather than tuned away.
- **Stop-and-ask trigger:** Removing a major contribution (e.g. AONT layer or CAP agent) or replacing the hypothesis requires the author's decision.

## DEC-005 — Replace proxy crypto with a complete AGP/1 protocol built on standard primitives
- **Date:** 2026-11-23
- **Issue:** R2 (protocol completeness), R1 (parameter sets, negotiation, native vs hybrid, handshake cost). No PQ code existed (BASELINE_AUDIT §3).
- **Alternatives:** (a) narrow the paper to "AES-GCM with assumed PQ key exchange"; (b) use TLS 1.3 with hybrid groups only; (c) implement a purpose-built handshake on library primitives.
- **Decision:** (c) for the proposed architecture, using `cryptography` 50.0.1 (statically linked OpenSSL 4.0.2; corrected 2026-11-23, KF-021) for ML-KEM, ML-DSA, X25519, AES-GCM, HKDF, X.509 — no primitive implemented from scratch. TLS 1.3 is used as a **baseline** (Milestone 7), not discarded.
- **Scientific impact:** PQ costs become measurements of this implementation instead of imported literature values. A custom handshake has not had the scrutiny TLS 1.3 has; this is stated as a limitation and the paper must not claim the protocol is proven secure.
- **Verification:** 46 security tests (`tests/security/test_protocol.py`); mutation smoke check (disabling replay, deadline or CA-signature checks makes ≥1 test fail).

## DEC-006 — ML-KEM-512 not offered
- **Date:** 2026-11-23
- **Issue:** R1 asks which ML-KEM parameter set is used.
- **Evidence:** `cryptography.hazmat.primitives.asymmetric.mlkem` exposes only `MLKEM768*` and `MLKEM1024*` classes in v50.0.1.
- **Decision:** Offer ML-KEM-768 (category 3, default) and ML-KEM-1024 (category 5). ML-KEM-512 results are reported as NOT YET EXPERIMENTALLY VERIFIED.

## DEC-007 — Benchmark scope and labelling
- **Date:** 2026-11-23
- **Decision:** All timing numbers are HARDWARE MEASUREMENTS on a virtualised x86-64 VM (EXP-002). They are not presented as embedded/RTU/Cortex-M results. If published embedded benchmarks are cited, they are labelled "external reference value" with source.

## DEC-008 — Replace the XOR "AONT"; add k-of-n erasure coding (scope change)
- **Date:** 2026-11-23
- **Issue:** R2: XOR transform is not IT-secure and needs a bound; all-fragments reconstruction is a DoS amplifier; evaluate erasure coding and multipath. EXP-001/EXP-004 show the legacy transform leaks 75–97 % of plaintext from N−1 fragments.
- **Alternatives:** (a) keep XOR and narrow the claim; (b) Shamir secret sharing (IT-secure, n× expansion); (c) package-transform AONT + Reed–Solomon (computational, ≈n/k expansion).
- **Decision:** (c). The legacy transform stays in `core/` only as the EXP-004 comparison. The layer is renamed "package-transform AONT" and the claim is computational (docs/fragmentation_aont.md §3). k-of-n erasure coding is a **scope addition**: k = n reproduces the original design; k < n is evaluated as the availability fix.
- **Scientific impact:** The "no information from partial sets" claim survives only as a computational, key-compromise-scoped statement. A negative finding is reported: burst loss is less harmful than i.i.d. loss for k = n (EXP-003), contrary to the manuscript.
- **Verification:** unit/integration tests (AONT round-trip, tamper rejection, MDS any-k decode, GE sampler equivalence, pipeline exactly-once delivery); EXP-003 abstraction check.

## DEC-009 — Constant-rate shaping leaks through timing; registered follow-up instead of tuning
- **Date:** 2026-11-23
- **Issue:** EXP-006 rejects the pre-run hypothesis: a classifier separates steady from active windows under shaping (AUC 0.79–0.83) via IAT tails, while KS on packet counts reports p = 1.0.
- **Decision:** Report EXP-006 as the primary result. Register EXP-010/011 *before* running: same attacker, new sessions (seed 10010), with fragmentation moved out of the emission loop (decoupled producer process) and the coupled 2 ms condition repeated as reference. Whatever EXP-011 shows is reported alongside EXP-006; no further iteration is made on the test sessions.
- **Scientific impact:** The manuscript claim "traffic indistinguishability (KS p > 0.93)" is withdrawn. Any revised claim is limited to the measured AUC with CI under the stated attacker.

## DEC-010 — CAP presented as an EWMA-type statistic (DECIDED BY THE AUTHOR)
- **Date:** 2026-11-23
- **Issue:** CAP_k = α·CAP_{k−1} + e_k equals EWMA/(1−α) (ANALYTICALLY DERIVED, unit-tested). EXP-007: CAP is not better than CUSUM (fewer false adaptations) or EWMA (faster on ramps).
- **Options put to the author (decision card):** reframe CAP as EWMA-based policy (recommended); drop L6; keep "novel metric" (not supported).
- **Decision (author, 2026-11-24):** reframe CAP as an EWMA-based adaptation policy. The manuscript already used this framing, so no text changed.

## DEC-011 — Cyber-physical study scope and U_safe
- **Date:** 2026-11-23
- **Decision:** AGC on the Andes IEEE 14-bus dynamic case; U_safe = hold the last validated set-point with primary droop active. Frequency limits from SOGL Annex III are used as illustrative limits (ASSUMPTION). Protection-class (≈3 ms) traffic is not studied in the plant model.
- **Finding requiring a design addition:** control-centre integrator wind-up during outages (EXP-008). Follow-up EXP-012 registered before running (integrator frozen without acknowledgements); both results reported.

## DEC-012 — TLS 1.3 baseline must authenticate both parties
- **Date:** 2026-11-23
- **Issue:** EXP-009 run_20261123T182344Z used server-only TLS authentication while AGP/1 authenticates both sides, so handshake bytes/time were not matched.
- **Decision:** keep that run (labelled server-auth only) and add mutual-auth TLS configurations (run_20261123T184325Z); the manuscript compares AGP/1 with mutual TLS.

## DEC-013 — Certificate chains in the mutual-TLS baseline
- **Date:** 2026-11-23
- **Issue:** after EXP-009 completed, inspection showed that OpenSSL auto-chaining includes the CA certificate (5442 B, ML-DSA-65) in both directions under mutual authentication, because each side's verify store contains the CA. AGP/1 sends end-entity certificates only. Python 3.13 exposes no switch for `SSL_MODE_NO_AUTO_CHAIN`, and `ChainCAFile` in the OpenSSL system-default configuration had no effect (tested).
- **Decision:** keep EXP-009 unchanged and state the caveat. Register EXP-013, which measures leaf-only chains via partial-chain trust of the peer's end-entity certificate (leaf pinning). This changes TLS trust semantics (no CA path validation), so EXP-013 is used only for the byte and CPU comparison, not as a deployable configuration.
- **Verification:** `test_tls13_mutual_autochain_sends_ca_and_leaf_only_does_not` asserts received chain lengths (2, 2) and (1, 1).

## DEC-014 — Outcomes of the registered follow-ups
- **Date:** 2026-11-23
- **EXP-011:** the shaping leak was an implementation effect; the manuscript reports both EXP-006 (leak) and EXP-011 (no detectable leak after decoupling) and states the minimum detectable AUC. The decoupled arrangement exists in the experiment runner (`producer_proc` in exp005_traffic_capture.py); in the library, `ConstantRateShaper` only emits and leaves fragmentation to the caller. Deployment guidance (manuscript §VII-D, docs/architecture.md) recommends decoupling. No further iteration on test sessions.
- **EXP-012:** control-centre anti-windup (freeze the AGC integrator while acknowledgements are missing) is added to the recommended deployment; it does not extend the safe hold time.
- **EXP-013:** the manuscript compares AGP/1 with chain-matched TLS bytes and in-memory CPU; EXP-009 wall times remain the socket-level comparison.

## DEC-015 — Repository layout for the v6 artefact
- **Date:** 2026-11-23
- **Issue:** the top level mixed v1–v5 code, one-off shell scripts, audit dumps and the v6 implementation; `ARTIFACT_ENTRYPOINT.md` pointed to a non-existent directory (KF-011) and CI masked failures (KF-008).
- **Decision:** move every legacy file unchanged into `legacy/` with `git mv` (history kept, nothing deleted). The only v6 dependency on legacy code is EXP-004, which now imports `legacy.core.fragmentation`; the frozen EXP-004 run is unaffected because its provenance records the commit that produced it. The broken `security_audit.yml` workflow is moved to `legacy/.github-workflows/`; `ci.yml` runs `verify_all.sh --smoke` in a Python 3.13 / OpenSSL 3.5 container. `setup.py` (legacy, pycryptodome) is replaced by `pyproject.toml` for `aegis_pq` and `baselines`.
- **Verification:** `verify_all.sh --smoke` after the move (FINAL_VALIDATION_REPORT.md).


## DEC-016 — Bounded fail-closed message reassembly (v6.1 candidate)
- **Date:** 2026-11-27
- **Issue:** The v6.0 receiver retained pending shards and delivered message IDs without global bounds; expiration depended entirely on explicit per-ID calls.
- **Decision:** Bound concurrent incomplete messages, aggregate shard bytes, per-message storage, message size, fragment count and delivered-ID history. Reject new work at capacity rather than evicting delivered IDs. Add a periodic-expiry API and lazy expiry on packet receipt.
- **Wire constraint:** The fragment header encodes n in u8; this implementation therefore caps n at 255 even though the underlying Reed-Solomon helper supports 256.
- **Message identity:** A sender never wraps its u32 message ID within a session. It must establish a new session after exhausting the ID space.
- **Consistency:** All fragments of one message share the same authenticated generation timestamp and deadline. Conflicting metadata or conflicting duplicate shards discard the incomplete message.
- **Verification status:** Code and regression tests added on `release/v6.1.0-rc1-hardening`; candidate CI and full verification remain pending.
- **Scientific impact:** These limits improve bounded resource behaviour but do not constitute a general DoS-resistance guarantee. Host applications must schedule `Receiver.expire_due()`.

## DEC-017 — AONT theorem claim withdrawn pending a complete reduction
- **Date:** 2026-11-27
- **Issue:** The previous proof sketch inferred a random-oracle query bound from a count of unknown output bits without establishing the adversary's view and shard-placement cases.
- **Decision:** Retain the transform and existing EXP-004 result, but withdraw the general theorem and any zero-leakage/proven-security language until a complete reduction and independent cryptographic review exist.
- **Evidence retained:** Implementation, unit tests, EXP-003 and EXP-004 remain in the repository. No raw experiment or legacy record is deleted.
- **Scientific impact:** The layer is described as an implemented package transform empirically evaluated against one specified partial-capture strategy; general security proof remains open.

## DEC-018 — Public repository is not equivalent to open-source licence
- **Date:** 2026-11-27
- **Issue:** Repository metadata describes the project as open-source, while `LICENSE` restricts use to academic contexts and prohibits redistribution.
- **Decision:** Do not silently replace the licence. Clarify the README and block a final public release until the author selects a licence compatible with intended reuse and journal policy.


## DEC-019 — Reject future-dated record generation timestamps
- **Date:** 2026-11-27
- **Issue:** The v6.0 receiver checked only the upper deadline bound. A valid authenticated sender could provide a future generation time and thereby extend the acceptance window.
- **Decision:** Reject a record when `t_gen > now + ε_clk`, in addition to the existing expiry check `now > t_gen + D + ε_clk`.
- **Verification status:** Regression test added on the v6.1 candidate; CI pending.
