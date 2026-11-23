# Baseline Audit — Aegis-Grid (Milestone 1)

Status: **COMPLETE** (Milestone 1 deliverable). Audit date: 2026-11-23 (UTC).
Auditor role: research-integrity remediation, branch `research-integrity-remediation`.

This document records the state of the repository and manuscript **before any
remediation**. Nothing on `main` or in any existing tag was modified. All
statements below cite the file, command, or raw output that supports them.

Evidence labels used throughout: `VERIFIED` (re-executed in this audit),
`CODE INSPECTION` (read, not executed), `NOT REPRODUCIBLE`, `NO SOURCE FOUND`.

---

## 1. Repository snapshot (Phase 0 freeze)

| Item | Value | Evidence |
|---|---|---|
| Remote | `https://github.com/BurhanAbdullah/aegis-grid` (public) | `git remote -v`; GitHub API `visibility=public` |
| Default branch | `main` | GitHub API |
| Audited commit | `65f83bf4bcfd496c0265d1e550f7dfc1177d68a3` (2026-03-18, "fix: final alignment with paper (XOR-AONT, CAP alpha=0.85, correct reconstruction simulation)") | `git log -1` |
| Tag at audited commit | `paper-v1-final` | `git ls-remote --tags` |
| Working tree at start | clean, no uncommitted changes | `git status` |
| Other remote branches | `audit-cleanup-2026` (5c21c7f), `paper-results-2026` (9d6b565), `paper-2026-assets` (0723952), `BurhanAbdullah-patch-1` (c8331aa), `release/v5-concept` (7de53cd) | `git ls-remote --heads` |
| Tags | 31 tags incl. `v1.0.0`, `v2.0`, `v3.0-*`, `v4.0-cyberphysical*`, `v5-concept`, `2026.1` (GitHub release), `paper-2026-*`, `paper-v1-final`, `research/v*-final` | `git ls-remote --tags` |
| Size | ~3.5 MB; 1,084 lines of Python (non-empty files), 1,764 lines of shell | `wc -l` |
| Remediation branch | `research-integrity-remediation`, created from `65f83bf` | this audit |

Preservation: the original manuscript is **not** committed (the repository is
public and the manuscript is unpublished). Its identity is recorded by hash in
§9. Existing CSVs, figures and scripts are left in place; new work goes into new
paths.

## 2. Environment used for the audit

| Item | Value |
|---|---|
| OS / kernel | Linux 6.18.44 x86_64, glibc 2.39 (cloud VM) |
| CPU | Intel Xeon @ 2.10 GHz, 4 vCPU (virtualised; frequency scaling not controllable) |
| Python | 3.13.18 |
| Legacy dependency | pycryptodome 3.23.0 (as pinned in `requirements.txt`) |

`requirements.txt` pins numpy 2.4.1 / matplotlib 3.10.8 / scipy 1.16.3 /
pycryptodome 3.23.0. `setup.py` declares only `pycryptodome`. No lock file, no
container definition, no seed registry.

## 3. Existing architecture (as implemented, not as described)

The README and manuscript describe a seven-layer pipeline (L1 PQ encryption → L2
AONT → L3 packet/dummy → L4 constant-rate emission → L5 deadline → L6 CAP agent →
L7 fail-secure). The code that exists for each layer:

| Layer | Code found | What it actually does (CODE INSPECTION unless marked) |
|---|---|---|
| L1 crypto | `core/crypto/encryption.py` (`AegisCrypt`, AES-GCM via pycryptodome); `core/crypto.py` (`CryptoEngine.encrypt = SHA-256(key‖data)`, `decrypt` returns input); `core/crypto/pki.py`, `core/crypto/ca.py` (RSA-2048 PKCS#1 v1.5 signatures) | No ML-KEM, no ML-DSA, no KEM handshake, no session-key derivation in any branch (`git grep` for ML-KEM/Kyber/Dilithium/mlkem: no hits). `core/crypto.py` is shadowed by the `core/crypto/` package and is unreachable. |
| Key schedule | `core/key_schedule.py` (HKDF-SHA256, RFC 5869 structure) | Correct HKDF structure, but its only caller `agents/secure_agent.py:get_layer_key` passes 2 args to a 3-arg function → `TypeError` (VERIFIED, EXP-000). |
| Authentication | `core/signature.py` (`SHA-256(key‖data)`), `core/auth.py` (HMAC-SHA256) | `SignatureEngine` is a keyed hash, not a signature; it is length-extension-prone as a MAC. `core/auth.py` HMAC is correct but unused by the protocol path. |
| L2 "AONT" | `core/fragmentation.py` | XOR with a random pad K of message length; pad K sent as the last fragment. **Not an AONT**: an adversary missing one masked fragment but holding K recovers 88.4 % of plaintext bytes on average (VERIFIED, EXP-001 probe 1). Reconstruction depends on fragment order (probe 1c) and produces empty fragments when message length < N−1 (probe 1d: 28 of 30 empty for a 14-byte message). |
| L3 packets/dummies | `core/packet.py`, `protocol/sender.py` | One fragment per **plaintext byte** in `protocol/sender.py`; dummy packets carry `msg_id + b"DUMMY"` as signable content (distinguishable by construction at the receiver). |
| L4 shaping | `network/traffic_shaper.py` | `time.sleep(window/len(packets))` per packet: interval depends on packet count, so emission rate is a function of message size (not constant-rate). No padding to fixed size. |
| L5 deadline | `core/timing.py`, `core/time_lock.py`, `protocol/secure_receive.py` | Wall-clock checks (`time.time()`); `secure_receive` uses a 5 s skew window and references an undefined `SecurityError`. |
| L6 CAP agent | `agents/secure_agent.py` | `cap = 0.85*cap + error`; if `cap ≥ 0.35` decrement N by 1 and ρ by 0.1. θ=0.35 in code vs θ=0.45 in manuscript. No normalisation of `error`, no reset/hysteresis. |
| L7 fail-secure | `core/v4/control.py` | `'execute' if status else 'drop'`. No plant, no U_safe, no safe set. `v4/scripts/*.sh` contain an ad-hoc shell "microgrid" with hand-set constants. |
| Replay protection | none in protocol path | `simulation/adversary.py` duplicates packets; no sequence-number window anywhere. |

## 4. Existing tests and their status (EXP-000, VERIFIED)

Command: `scripts/research_integrity/run_legacy_entrypoints.sh`. Raw logs:
`results/raw/EXP-000_legacy_entrypoints/`.

| Command | Exit | Outcome |
|---|---|---|
| `python3 main.py` | 0 | Runs; prints success ratios 0.23/0.02/0.01/0.00 at loss 10–40 % (100 unseeded trials) |
| `python3 -m tests.verify_v1` | 1 | `AttributeError: SecureAgent has no attribute add_attack_pressure` |
| `python3 -m tests.verify_v2` | 1 | `ImportError: SecureAgentV2` |
| `python3 -m tests.verify_final` | 1 | `ImportError: verify_indistinguishability` |
| `python3 verify_model.py` | 0 | Only checks that files exist; reports `OBJECTIVES_LOG.md` MISSING |
| `python3 generate_validation.py` | 1 | `KeyError: 'latency'` |
| `python3 -m pytest -q tests` | 5 | "no tests ran" (no `test_*.py` files) |
| `SecureAgent(...).get_layer_key(1)` | 1 | `TypeError` (key-schedule call mismatch) |

CI (`.github/workflows/ci.yml`) masks failures: `pip install ... || echo`,
`py_compile ... || echo "SYNTAX ERROR"`, `pytest ... || true`, `flake8 ... || true`.
A green CI badge therefore carries no information. **Existing automated test
coverage of the research claims: none.**

## 5. Existing experimental evidence and provenance

| Manuscript figure | Data source located | Generator | Status |
|---|---|---|---|
| Fig. 1, Fig. 2 (architecture) | diagrams | n/a | Conceptual; overlapping content (Reviewer 1) |
| Fig. 3 reconstruction vs loss | analytic `(1−p)^N` (`paper_artifacts/enhanced_scripts/generate_reconstruction.sh`) | closed form | ANALYTICAL; plot shows N=30 but caption says N∈{5,10,20} |
| Fig. 4 MC 95 % CI | `paper_artifacts/journal_data/monte_carlo_ci.csv` | `monte_carlo_ci.sh` (unseeded) | Re-runnable but **NOT REPRODUCIBLE bit-for-bit** (no seed); Wald CI gives negative lower bounds in 3 rows and zero-width intervals at mean 0 in 10 rows (EXP-001 probe 3) |
| Fig. 5 "Markov burst-loss" | `journal_data/stochastic_loss.csv` | `stochastic_loss.sh` | **INCONSISTENT**: the script draws an independent state each step (i.i.d. loss), not a Gilbert–Elliott chain; stored values match (1−p)^20 within |z|<2 (probe 2) |
| Fig. 6 mutual information | `scripts/gen_v3_information_leakage_csv.py` | writes `0.0` for every row | **NO MEASUREMENT** — hard-coded zeros |
| Fig. 7 traffic + KS p>0.93 | none matching; `scripts/gen_v3_traffic_csv.py` writes active=idle=10 | none | **NO SOURCE FOUND** for plotted data or KS test (no `ks_2samp`/Kolmogorov code in any branch) |
| Fig. 8 latency static vs adaptive (48/35 ms) | `paper_artifacts/data/v3_latency_comparison.csv` (static max 56 ms, agent max 33 ms) | `scripts/gen_v3_latency_compare_csv.py` writes constant 48/35 | **INCONSISTENT / NO MEASUREMENT**: the 48 ms and 35 ms in the text come from hard-coded constants; the plotted CSV has no generator and contradicts the text (static exceeds 50 ms) |
| Fig. 9 CAP timeline | none | none | **NO SOURCE FOUND** |
| Fig. 10 θ sensitivity (θ*=0.45) | none | none | **NO SOURCE FOUND** |
| Fig. 11 fail-secure trajectory | `paper_artifacts/data/v4_control_safety.csv` (unitless 0–1 values); `scripts/gen_v4_safety_csv.py` writes a hand-written step | none for plotted data | **NO PLANT MODEL** |
| Fig. 12 O(N) timing, <45 ms | none | none | **NO SOURCE FOUND**; no timing code |
| Fig. 13 radar comparison | none | none | Qualitative scores with no stated basis |
| Table 4/6 baselines | `paper_artifacts/data/baseline_comparison.csv` (normalised scores, e.g. AegisGrid TrafficLeakage 0.0) | none | Hand-assigned scores; `docs/IMPLEMENTATION_STATUS.md` itself states baseline comparisons are "analytical and model-based" |

`docs/FIGURE_PROVENANCE.md` and `paper_results/2026/README.md` state that all
figures are generated from simulation outputs without manipulation. The
findings above contradict that statement for Figs. 6–13.

Other legacy result generators with literal data: `generate_plots.py`,
`comparison/benchmark.py`, `simulation/run_ieee_plots.sh`,
`simulation/run_ieee_adaptivity.sh` (lists of numbers typed into the script,
e.g. `throughput = [950, 820, 650, 480]`). `docs/SIMULATION_METHODOLOGY.md`
states emission is a Poisson process, contradicting the manuscript's fixed-rate
emission.

## 6. Existing research claims (manuscript, abbreviated)

Detailed claim-by-claim mapping is in `CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md` §B.
Headline claims: PQ protection with ML-KEM/ML-DSA (FIPS 203/204); AONT with
negligible mutual information for any strict subset; traffic indistinguishability
(KS p>0.93); worst-case latency 48 ms static / 35 ms adaptive; all properties under
a 50 ms bound with "proven 5 ms safety margin"; θ*=0.45 with ≈0 false adaptations;
fail-secure trajectory stays in S_safe; "simulations and emulations"; O(N) scaling
<45 ms; 2000 Monte Carlo trials; Markov burst-loss evaluation.

## 7. Known inconsistencies (summary)

1. No post-quantum code exists; the manuscript describes measured PQ behaviour.
2. "AONT" is XOR one-time-pad + key fragment; not an AONT (measured leakage 88 %).
3. KS test, MI computation, CAP timeline, θ sweep, O(N) timing: no code anywhere.
4. Latency numbers 48/35 ms are constants typed into a generator script.
5. "Markov burst loss" is i.i.d. loss.
6. θ = 0.35 in code vs 0.45 in manuscript.
7. 4 ms GOOSE motivation vs 50 ms evaluated bound (Reviewer 2).
8. Manuscript claims emulation; Section "Planned emulated evaluation" says it is planned only.
9. Legacy tests fail; CI suppresses failures.
10. `ARTIFACT_ENTRYPOINT.md` names `Aegis-Grid-Unified/core/` as the primary artifact; that directory does not exist on `main`.
11. Manuscript reference list: duplicates ([1]=[30], [13]=[20], [22]=[33]); AONT citation in text points to [18] (a vendor web page) instead of [24]; Rivest's original AONT paper not cited.

## 8. Missing components

ML-KEM/ML-DSA handshake; certificate validation; session-key derivation wiring;
nonce/sequence management; replay window; rekeying; downgrade protection; a real
AONT; erasure coding / redundancy; fixed-size padding; any traffic trace capture;
any attacker classifier; CAP normalisation and baselines (EWMA/CUSUM); any plant
model; any measured timing; seeds/configs/experiment records; meaningful tests.

## 9. Current manuscript status

| Item | Value |
|---|---|
| Submitted version | IJIS submission 15 May 2026, rejected 23 Nov 2026 (Reviewer 1 & 2 reports available to the authors) |
| Text audited | Author's Drive file `ieee paper3.docx` (IEEE Access template, last modified 2026-04-23), SHA-256 `9c757ef5841782bbb177ccf579471b10900dca607f7346be5c8e3eecb7066112`. Content matches every passage quoted by Reviewer 2. If the exact IJIS PDF differs, the audit must be re-checked against it (ASSUMPTION). |
| Stored in repo | No (public repository; unpublished manuscript) |

## 10. Reproducibility status (baseline)

**NOT REPRODUCIBLE** for the manuscript as a whole: the majority of reported
numbers (Figs. 6–13, Tables 4–6, headline latency values, KS p-value, θ*) have no
generating code. Figs. 3–5 are re-runnable but unseeded, and Fig. 5 does not
implement the model it is labelled with.

## 11. Consequence for the remediation plan

Every quantitative statement in the revised manuscript must come from new,
seeded, recorded experiments (Milestones 2–7). Legacy figures are retained in
the repository for provenance but are not used as evidence. See
`DECISION_LOG.md` DEC-001…DEC-004.
