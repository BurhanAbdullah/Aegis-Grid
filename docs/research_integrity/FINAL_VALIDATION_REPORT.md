# Final Validation Report (Milestone 9)

Date: 2026-11-23 (UTC). Branch `research-integrity-remediation`, release tag
`v6.0-revision`. This report states what was verified, how, and what remains
open. It does not claim more than the listed evidence supports.

## 1. One-command verification

`./scripts/verify_all.sh --smoke` on the reference environment, after the
repository cleanup (commit `64e68f0`), exit status 0:

| Stage | Status | Detail |
|---|---|---|
| environment (pinned versions) | PASS | `requirements-remediation.txt` matched; Python `ssl` on OpenSSL 3.5 |
| compile aegis_pq, baselines, experiments | PASS | |
| pytest (unit, integration, security) | PASS | 102 passed |
| mutation: replay window | PASS | disabled check detected by the tests |
| mutation: deadline check | PASS | disabled check detected |
| mutation: AONT canary | PASS | disabled check detected |
| mutation: shaper late drop | PASS | disabled check detected |
| result provenance files | PASS | every run directory has config, environment and status |
| manuscript numbers vs results | PASS | 1124 manuscript values re-derived from 10 result runs and identical to `results/paper_values.json` |
| smoke runs EXP-002, 003, 004, 005, 006, 007, 008, 009, 013 | PASS | reduced configurations, written to a temporary directory |
| embedded / RTU hardware benchmarks | BLOCKED | no embedded hardware available |

EXP-010, EXP-011 and EXP-012 use the EXP-005, EXP-006 and EXP-008 runners with
other configurations, so the smoke runs of those runners cover their code paths.

Reference environment: Intel Xeon @ 2.10 GHz virtual machine (x86-64), Python
3.13.18, `cryptography` 50.0.1 (statically linked OpenSSL 4.0.2), Python `ssl` on
OpenSSL 3.5.9, scikit-learn 1.9.1, ANDES 2.0.0.

## 2. Experiments

| ID | Question | Result | Evidence label |
|---|---|---|---|
| EXP-000/001 | Do the legacy entry points and claims hold? | 6 of 8 entry points fail; XOR transform leaks plaintext | VERIFIED (audit) |
| EXP-002 | PQ primitive and handshake CPU cost | handshake 0x0101 3.72 ms CPU (median, both parties), 20 042 B | HARDWARE MEASUREMENT (x86-64 VM) |
| EXP-003 | Delivery under i.i.d. and burst loss | 10 % loss: k = n = 5 0.596 → RS(5,7) 0.977; Gilbert 10 %, burst 5: 0.82 → 0.885 | SIMULATION RESULT |
| EXP-004 | Plaintext recovery from partial captures | XOR 0.75–0.97 of bytes; package-transform AONT ≈ 0.004 (chance level) | SIMULATION RESULT + ANALYTICALLY DERIVED bound |
| EXP-005/006 | Traffic-analysis attacker vs shaping | shaped 2 ms: AUC 0.77–0.82 (leak, KF-015) | HARDWARE MEASUREMENT (loopback) |
| EXP-010/011 | Decoupled shaping (registered follow-up) | coupled leak reproduced (0.73–0.77); decoupled 0.48–0.56, below the minimum detectable AUC | HARDWARE MEASUREMENT (loopback) |
| EXP-007 | CAP vs CUSUM, EWMA, Shewhart | CAP not better than CUSUM or EWMA (KF-017) | SIMULATION RESULT |
| EXP-008/012 | Fail-secure AGC on IEEE 14-bus | forged commands rejected; hold time bounded; anti-windup removes overshoot | SIMULATION RESULT; limits are ASSUMPTION (SOGL) |
| EXP-009/013 | AGP/1 vs TLS 1.3 and HMAC | AGP/1 5.74 ms vs TLS hybrid mutual 4.79 ms wall; chain-matched TLS 20 546 B vs AGP/1 20 042 B | HARDWARE MEASUREMENT (loopback) |

Failed and superseded runs are kept and listed in `EXPERIMENT_REGISTER.md`.
EXP-002/003/004 were rerun on a clean tree; the stochastic EXP-003/004 reruns are
identical to the development runs.

## 3. Claims

All 20 audited claims of the earlier manuscript (C1–C20) have a final status in
`CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md`: implemented and measured (C1, C11,
C12, C14), replaced (C5, C18), scoped or qualified (C4, C9), withdrawn (C7, C8),
removed (C2, C3, C10, C13, C16, C17), rewritten or fixed (C6, C15, C19, C20).

## 4. Reviewer comments

Every comment of Reviewer 1 (R1.1–R1.8) and Reviewer 2 (R2.1–R2.13) has a response
and a corresponding change in the revised manuscript. The response letter is
generated from the same `results/paper_values.json` and reference numbering as
the manuscript, so the numbers in both documents are identical by construction.
The manuscript and the reviewer text are kept outside this public repository.

## 5. Readiness assessment

**Technically ready:** the implementation, tests, raw results and the mapping
from results to every manuscript number are complete and reproducible with one
command.

**Requires the author before submission:**

1. **Authors and affiliations.** The manuscript lists one author (Burhan U Din
   Abdullah), as in the earlier version. The earlier submission was handled by a
   different corresponding author. The author list, affiliations, funding and
   corresponding author must be confirmed.
2. **References.** Fifty references were checked against bibliographic sources.
   Eight details could not be confirmed: the exact title of the Gonçalves et al.
   entry, the volume and pages of Page (1954), Roberts (1959), Gilbert (1960),
   Elliott (1963) and Cliff (1993), and the issue number of the ANDES paper. Each
   is marked in the reference audit file delivered with the manuscript.
3. **CAP framing (DEC-010).** The revision presents CAP as an EWMA-based
   adaptation policy and reports that it does not detect better than CUSUM or
   EWMA. This changes a contribution of the earlier paper and needs the author's
   scientific confirmation.
4. **Journal template.** The manuscript uses the template of the earlier
   submission (IEEE Access style). If it is submitted to a different journal, the
   journal's own template applies.
5. **Licence.** `LICENSE` states "academic use only, redistribution prohibited".
   The Data and Code Availability statement points to this repository; the
   author should check that this licence meets the target journal's
   data-availability policy.

**Limits that remain after revision (stated in the manuscript):**

- No embedded or RTU hardware measurements; all timings are from one virtualised
  x86-64 server. Protection-class messages (about 3 ms) are a stress point, not a
  supported use.
- The decoupled shaper shows no detectable leak at the tested sample size; this
  is a null result with a stated minimum detectable effect, not a proof of
  indistinguishability. Shaping at Δ = 2 ms delivers only 43 % of
  20 ms-deadline event messages (KF-016).
- Every detector raises false adaptations in benign congestion (KF-017).
- The plant study bounds the safe hold time; it does not prove that the plant
  remains in a safe set in general.
- All experiments were run in one remediation session on one machine and have
  not been replicated independently.
- The GitHub Actions workflow was rewritten but its first run happens when the
  branch is pushed; its result is reported on the pull request.
