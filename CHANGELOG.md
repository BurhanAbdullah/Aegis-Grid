# Changelog

All notable changes to Aegis-Grid are documented here.
Tags are frozen research states. Releases are archival snapshots for citation.

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

See README.md section 10 for the full tagging philosophy.
