# Aegis-Grid v6

Research artefact for the manuscript *A Time-Bounded and Fail-Secure Post-Quantum
Communication Architecture for Supervisory and Wide-Area Smart Grid Control:
Design, Implementation and Measured Trade-offs*. The prior v6.0 research
baseline is preserved. The branch `release/v6.1.0-rc1-hardening` contains
corrective work under review and is not a final release.

Aegis-Grid is a layered communication architecture for control messages in smart
grids. A message is useful only if it is authentic, fresh and delivered within the
deadline of its traffic class; otherwise the receiver discards it and applies a
predefined safe input. This repository contains the implementation, the
experiments, the raw results of every registered run, and the scripts that turn
those results into the figures and numbers of the manuscript.

## What is implemented

| Layer | Mechanism | Code |
|---|---|---|
| L1 | AGP/1 handshake: ML-KEM (FIPS 203) + ML-DSA (FIPS 204), optional X25519 hybrid, X.509 with a pinned CA | `aegis_pq/handshake.py`, `pki.py`, `suites.py` |
| L1/L5 | AES-256-GCM records with a sliding replay window and an authenticated deadline | `aegis_pq/channel.py`, `clock.py` |
| L2 | Package transform with Reed–Solomon k-of-n coding; general AONT security proof remains open | `aegis_pq/aont.py`, `erasure.py`, `pipeline.py` |
| L3/L4 | Constant-rate shaper (fixed-size records, interval Δ, encrypted dummies, late drop) | `aegis_pq/shaping.py` |
| L6 | Cumulative attack pressure (CAP, an EWMA-type statistic) and CUSUM/EWMA/Shewhart baselines | `aegis_pq/detectors.py` |
| L7 | Receiver fail-secure fallback evaluated on the IEEE 14-bus system (ANDES) | `experiments/runners/exp008_cyberphysical_agc.py` |
| Baselines | TLS 1.3 (classical, ML-KEM, hybrid; server-only and mutual authentication), IEC 62351-6-style HMAC | `baselines/` |

Post-quantum primitives come from `cryptography` 50.0.1; nothing is implemented
from scratch and no external benchmark values are used. The evidence class of
every claim (hardware measurement, simulation result, analytically derived,
assumption) is listed in
[`docs/research_integrity/CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md`](docs/research_integrity/CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md).

## Quick start

```bash
python3.13 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt     # exact versions used for all registered runs
./scripts/verify_all.sh                          # environment, tests, mutation checks, provenance, manuscript numbers, figures
./scripts/verify_all.sh --smoke                  # + reduced runs of every experiment runner (about 5 min)
```

The TLS baseline needs a Python whose `ssl` module is linked against OpenSSL 3.5
or later (ML-KEM key exchange groups and ML-DSA certificates); `verify_all.sh`
checks this. Every stage prints PASS, FAIL, SKIPPED, NOT RUN or BLOCKED; the
embedded-hardware stage is BLOCKED because no device was available.

## Repository layout

```
aegis_pq/          protocol implementation (AGP/1, AONT, erasure coding, shaping, detectors)
baselines/         TLS 1.3 and IEC 62351-6-style HMAC baselines
experiments/       runners and JSON configurations (EXP-002 ... EXP-014), smoke configurations
results/raw/       one directory per run: config, environment, status, raw CSV/JSON outputs
results/paper_values.json   every number quoted in the manuscript, derived from results/raw
figures/           600 dpi PNG + PDF + CSV for each figure; diagrams/ holds draw.io sources
scripts/           verify_all.sh, paper_values.py, make_figures.py, make_diagrams.py, checks
tests/             unit, integration, security and regression tests (pytest)
docs/              architecture, protocol, threat model, methodology, limitations, research-integrity records
data/external/     published third-party values (pqm4 cycle counts), labelled as external
legacy/            earlier versions (v1–v5) kept unchanged for traceability; not used for v6 results
```

## Reproducing the results

Each experiment is one runner plus one configuration with a fixed seed:

```bash
python3 experiments/runners/exp003_reliability.py experiments/configs/EXP-003_reliability.json
python3 scripts/paper_values.py     # regenerate results/paper_values.json
python3 scripts/make_figures.py     # regenerate figures/
```

The full list, run times and determinism notes are in
[`docs/reproducibility.md`](docs/reproducibility.md). Stochastic experiments
reproduce exactly from their seeds on the pinned versions; timing experiments
reproduce in distribution only and depend on the hardware.

## Research-integrity records

| File | Content |
|---|---|
| [`EXPERIMENT_REGISTER.md`](docs/research_integrity/EXPERIMENT_REGISTER.md) | hypothesis, configuration and outcome of every run, including failed and superseded runs |
| [`CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md`](docs/research_integrity/CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md) | status of each manuscript claim and the evidence behind it |
| [`KNOWN_FAILURES.md`](docs/research_integrity/KNOWN_FAILURES.md) | open and closed defects, including negative results |
| [`DECISION_LOG.md`](docs/research_integrity/DECISION_LOG.md) | design and methodology decisions with their reasons |
| [`BASELINE_AUDIT.md`](docs/research_integrity/BASELINE_AUDIT.md) | audit of the earlier version before remediation |
| [`AUDIT_LOG.md`](docs/research_integrity/AUDIT_LOG.md) | chronological log of the remediation |
| [`FINAL_VALIDATION_REPORT.md`](docs/research_integrity/FINAL_VALIDATION_REPORT.md) | final verification and readiness assessment |

## Scope and limitations

All timings are measurements on a virtualised x86-64 server, not on embedded
devices or RTUs. Protection-class messages (about 3 ms transfer time) are a stress
point only. Traffic shaping showed a measurable activity leak when fragmentation
shared the emission loop (EXP-006); decoupling the producer removed any detectable
leak at the tested sample size (EXP-011), which is not a proof of
indistinguishability. See [`docs/limitations.md`](docs/limitations.md).

## Citation

Citation metadata is in [`CITATION.cff`](CITATION.cff). Security reporting is
described in [`SECURITY.md`](SECURITY.md) and changes in [`CHANGELOG.md`](CHANGELOG.md).

## Licence and reuse

This is a public research repository, but the current `LICENSE` says
"academic use only" and prohibits redistribution. It is **not** an OSI-approved
open-source licence. Reuse, redistribution and journal data-availability
permissions must be resolved by the author before a public release. No licence
change is made by this remediation branch.

## v6.1.0 release candidate

The hardening candidate adds bounded message reassembly, automatic expiry
support, consistent per-message generation/deadline metadata, explicit resource
rejection and regression tests. The caller must schedule
`Receiver.expire_due()` periodically; lazy expiry on packet receipt alone is
not a substitute for a timer. See
[`docs/release/V6.1.0_RC1_READINESS.md`](docs/release/V6.1.0_RC1_READINESS.md)
and [`docs/security_review_register.md`](docs/security_review_register.md).
