import csv

out = "paper_results/2026/csv/v3_agent_adaptation.csv"

with open(out, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "N", "rho", "latency"])
    for t in range(50):
        if t < 25:
            writer.writerow([t, 10, 1.0, 30])
        else:
            writer.writerow([t, 20, 2.0, 45])

print("[OK] v3 agent CSV generated")
