import csv

out = "paper_results/2026/csv/v3_traffic_entropy.csv"

with open(out, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "active", "idle"])
    for t in range(50):
        writer.writerow([t, 10, 10])

print("[OK] v3 traffic CSV generated")
