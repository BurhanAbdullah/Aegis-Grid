import csv, random

random.seed(2)

loss_rates = [0, 0.05, 0.1, 0.2, 0.3, 0.4]
Ns = [5, 10, 20]

out = "paper_results/2026/csv/v2_reconstruction.csv"

with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["packet_loss", "N", "success_probability"])
    for N in Ns:
        for p in loss_rates:
            success = max(0, 1 - (p * N * 1.5))
            w.writerow([p, N, round(success, 2)])
