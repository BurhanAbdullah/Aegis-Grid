# Changelog

All notable changes to Aegis-Grid are documented here.  
This file follows the research versioning philosophy described in `README.md`.  
Tags represent frozen research states; releases represent archival snapshots.

---

## [2026.1] — 2026-01-24
**Release:** Aegis-Grid Research Package 2026.1  
First public archival release. Captures the complete v1–v5 research sequence,
Monte Carlo simulation results, formal security theorems, and the accompanying
paper draft.

### Included Research States
- `v1` — Baseline Fail-Secure (Rigid): deterministic, no adaptation
- `v2` — Adaptive Thresholding Under Pressure: CAP-bounded parameter tuning
- `v2_model` — Extended v2 model artefacts
- `v3` — Agentic Elastic Defense: autonomous agent layer (L6)
- `v3.3` — Extended Cyber-Physical Timing: tight physical deadline coupling
- `v4` — Grid-Aware Security Constraints: grid-state-derived policies
- `v5` — Quantum-Adversarial (Max Resilience): conceptual post-cryptographic model

### Repository Improvements (post-initial-release)
- Removed `error_log.txt` from version control
- Removed `aegis_grid.egg-info/` from version control
- Renamed `Pressure:` → `Pressure.md` (cross-platform compatibility)
- Comprehensive `.gitignore` added
- GitHub Actions CI pipeline added
- `CHANGELOG.md` added
- Version tags applied to each research state

---

## How to Cite a Specific Research State

```bash
git checkout tags/<tag-name>
```

See `README.md` § 10 for the full tagging and release philosophy.
