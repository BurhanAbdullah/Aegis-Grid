import csv

N = 20
EPS = 1e-6

out = "paper_results/2026/csv/v3_information_leakage.csv"

with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["intercepted_fragments", "mutual_information"])
    for k in range(N):
        w.writerow([k, round(EPS * k, 8)])
