import csv

out = "paper_results/2026/csv/v4_control_safety.csv"

with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time", "state_normal", "state_under_attack"])
    for t in range(50):
        normal = 1.0
        attack = 1.0 if t < 20 else 0.2
        w.writerow([t, normal, attack])
