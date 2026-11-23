# Aegis-Grid — Artifact Entry Point (v6.0-revision)

All results of the revised manuscript come from the code at the top level of this
repository. Earlier research states (v1–v5) are kept unchanged under `legacy/` for
traceability and are **not** used for any v6 result, except the legacy XOR
fragmentation (`legacy/core/fragmentation.py`), which EXP-004 evaluates as the
baseline that the package-transform AONT replaces.

| Purpose | Location |
|---|---|
| Verify everything with one command | `./scripts/verify_all.sh [--smoke]` |
| Protocol implementation | `aegis_pq/` |
| Baselines (TLS 1.3, IEC 62351-6-style HMAC) | `baselines/` |
| Experiment runners and configurations | `experiments/runners/`, `experiments/configs/` |
| Raw results with provenance (config, environment, status) | `results/raw/EXP-0xx/run_*/` |
| Every number quoted in the manuscript | `results/paper_values.json` (`scripts/paper_values.py`) |
| Figures (600 dpi PNG, PDF, CSV) and draw.io diagrams | `figures/`, `figures/diagrams/` |
| Experiment register, claim matrix, known failures, decisions | `docs/research_integrity/` |
| Reproduction instructions | `docs/reproducibility.md` |

Manuscript tables and figures map to experiments as listed in
`docs/research_integrity/EXPERIMENT_REGISTER.md` and `figures/FIGURE_SOURCES.csv`.
