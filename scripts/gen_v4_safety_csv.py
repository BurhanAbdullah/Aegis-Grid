import csv

out = "paper_results/2026/csv/v4_control_safety.csv"

with open(out, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "normal", "attack"])
    for t in range(50):
        writer.writerow([t, 1.0, 1.0 if t < 20 else 0.0])

print("[OK] v4 safety CSV generated")
