import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("paper_results/2026/csv/baseline_comparison.csv")

metrics = df.columns[1:]
x = range(len(metrics))

plt.figure(figsize=(8,5))

for i, row in df.iterrows():
    plt.plot(x, row[1:], marker='o', label=row['System'])

plt.xticks(x, metrics, rotation=20)
plt.ylim(0,1)
plt.ylabel("Normalized Score")
plt.title("Quantitative Baseline Comparison (Model-Based)")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("paper_results/2026/figures/fig_baseline_comparison.png", dpi=300)
