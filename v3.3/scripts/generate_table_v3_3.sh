#!/usr/bin/env bash
set -e

python <<'PYCODE'
import pandas as pd

sweep = pd.read_csv("results_v3.3/delay_sweep.csv")
baseline = pd.read_csv("results_v3.3/baseline_vs_failsecure.csv")
ieee39 = pd.read_csv("results_v3.3/ieee39_results.csv")

print("\n=== LaTeX Results Table ===\n")

print("\\begin{tabular}{lcc}")
print("\\toprule")
print("Scenario & Delay (ms) & Acceptance \\\\")
print("\\midrule")

for _, r in sweep.iterrows():
    print(f"IEEE-14 Sweep & {int(r['delay_ms'])} & {r['acceptance_ratio']:.2f} \\\\")

for _, r in baseline.iterrows():
    label = r["mode"].replace("_", "-")
    print(f"{label} & 80 & {r['acceptance_ratio']:.2f} \\\\")

print(f"IEEE-39 & 60 & {ieee39['acceptance_ratio'].iloc[0]:.2f} \\\\")
print("\\bottomrule")
print("\\end{tabular}")
PYCODE
