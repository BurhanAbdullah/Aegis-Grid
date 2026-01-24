import csv, random

random.seed(3)

out = "paper_results/2026/csv/v3_traffic_entropy.csv"

with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time", "active", "idle"])
    for t in range(50):
        base = 10
        w.writerow([
            t,
            base + random.uniform(-0.3, 0.3),
            base + random.uniform(-0.3, 0.3)
        ])
