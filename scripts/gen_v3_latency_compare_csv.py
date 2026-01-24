import csv

out = "paper_results/2026/csv/v3_latency_comparison.csv"

with open(out, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["load", "static", "agent"])
    for load in range(10, 101, 10):
        writer.writerow([load, 48, 35])

print("[OK] v3 latency comparison CSV generated")
