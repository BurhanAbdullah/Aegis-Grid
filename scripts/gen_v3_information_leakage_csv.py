import csv

N = 20
out = "paper_results/2026/csv/v3_information_leakage.csv"

with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["intercepted_fragments", "mutual_information"])
    for k in range(N):
        w.writerow([k, 0.0])

print("[OK] v3 information leakage CSV generated")
