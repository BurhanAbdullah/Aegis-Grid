# Results

## `raw/`

One directory per registered run, `raw/EXP-0xx/run_<UTC timestamp>/`, holding:

| File | Content |
|---|---|
| `config.json` | the exact configuration, including the seed |
| `environment.json` | Python and package versions, OpenSSL versions, CPU, commit |
| `status.json` | `COMPLETED`, `FAILED` or a note that the run is superseded, and why |
| other files | raw outputs (CSV, JSON, compressed time series) |

Runs are never edited or deleted. A run that was replaced, for example a
development run repeated on a clean tree, keeps its directory and says so in
`status.json`. `EXP-000_legacy_entrypoints` and `EXP-001_audit_probes` are the
logs of the audit of the earlier version. The commit recorded in
`environment.json` may exist only on a pull-request branch, because pull requests
are squash-merged: `research-integrity-remediation` (EXP-002 to EXP-013) and
`fix-attacker-feature-count` (EXP-014). Both branches are kept for that reason.

## `paper_values.json`

Every number quoted in the manuscript, derived from `raw/` by
`scripts/paper_values.py`. `scripts/verify_all.sh` re-derives the file and checks
that it is unchanged. Its `_sources` entry lists the runs the values are derived
from; hypotheses and outcomes of every run, including failed and superseded ones,
are in [`docs/research_integrity/EXPERIMENT_REGISTER.md`](../docs/research_integrity/EXPERIMENT_REGISTER.md).
