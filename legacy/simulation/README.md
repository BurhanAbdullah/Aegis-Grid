# simulation/

Simulation harness for Aegis-Grid experiments.

## Purpose

Provides the execution environment for all versioned research stages.
Simulations are model-based — they do not connect to real grid infrastructure.

## Key Scripts

| Script | Purpose |
|--------|---------|
| `run_ieee_adaptivity.sh` | IEEE-format adaptivity experiment |
| `run_ieee_plots.sh` | Generate IEEE-format figures |

## Reproducibility

All simulations are deterministic given fixed parameters.
Parameters are version-scoped and declared in each version's README.

No smoothing, curve fitting, or post-hoc data removal is applied.
Raw output is written directly to `paper_results/2026/`.

## Running Simulations

```bash
# Full simulation suite
bash simulation/run_ieee_adaptivity.sh

# Generate figures only
bash simulation/run_ieee_plots.sh
```

## Output

Figures are written to `paper_results/2026/`.
Raw data is written to `data/`.
