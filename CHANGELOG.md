# Changelog

All notable changes to Aegis-Grid are documented here.
Tags are frozen research states. Releases are archival snapshots for citation.

---

## [6.0.0] - 2026-11-23 (tag v6.0-revision)

Revision in response to the reviews of the IJIS submission. Research-integrity
remediation: every result is re-measured on a working implementation.

### Added
- `aegis_pq/`: AGP/1 handshake (ML-KEM, ML-DSA, optional X25519 hybrid), AES-256-GCM
  records with replay window and authenticated deadline, package-transform AONT with
  Reed–Solomon k-of-n coding, constant-rate shaper, CAP and CUSUM/EWMA/Shewhart detectors.
- `baselines/`: TLS 1.3 (classical, ML-KEM, hybrid; server-only and mutual) and
  IEC 62351-6-style HMAC.
- Registered experiments EXP-002 to EXP-014 with raw outputs and provenance in `results/raw/`.
- `scripts/verify_all.sh`, `scripts/paper_values.py`, `scripts/check_manuscript_numbers.py`,
  600 dpi figures and draw.io diagrams.
- 102 unit, integration and security tests; research-integrity records in `docs/research_integrity/`.

### Changed
- v1–v5 code, scripts, data and documents moved unchanged to `legacy/` (`git mv`).
- CI runs `verify_all.sh --smoke` on Python 3.13 / OpenSSL 3.5; failures fail the job.
- Packaging moved from `setup.py` to `pyproject.toml`.
- Repository cleanup: pinned versions in `requirements.txt` (was `requirements-remediation.txt`),
  pytest configuration in `pyproject.toml`, stray editor and tool state removed,
  `CITATION.cff` and folder READMEs added, `SECURITY.md` rewritten for v6.
- `scripts/check_figures.py` (run by `verify_all.sh`): every committed figure is regenerated
  from the committed runs into a temporary directory and compared byte for byte.

### Withdrawn claims
- See `docs/research_integrity/CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md` and
  `KNOWN_FAILURES.md` (traffic indistinguishability, XOR AONT security, CAP novelty,
  guaranteed safe plant behaviour).

---

## [2026.1] - 2026-01-24

First public archival release. Captures the complete v1-v5 research sequence,
Monte Carlo simulation results, formal security theorems, and paper draft.

### Research States
- v1   - Baseline Fail-Secure (Rigid): deterministic, no adaptation
- v2   - Adaptive Thresholding Under Pressure: CAP-bounded tuning
- v3   - Agentic Elastic Defense: autonomous agent layer (L6)
- v3.3 - Extended Cyber-Physical Timing: tight physical deadline coupling
- v4   - Grid-Aware Security Constraints: grid-state-derived policies
- v5   - Quantum-Adversarial (Max Resilience): post-cryptographic model

### Repo Hygiene (post-release)
- Removed error_log.txt from version control
- Removed aegis_grid.egg-info/ from version control
- Renamed 'Pressure:' to Pressure.md (cross-platform fix)
- Comprehensive .gitignore added
- GitHub Actions CI pipeline added
- CHANGELOG.md added
- Research-state tags applied to v1-v5

---

## Checkout a specific research state

    git checkout tags/research/v3-final

Research states v1–v5 are also kept unchanged under `legacy/`.
