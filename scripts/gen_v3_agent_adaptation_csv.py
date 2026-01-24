import csv

N, rho = 10, 1.0

out = "paper_results/2026/csv/v3_agent_adaptation.csv"

with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time", "N", "rho", "latency"])
    for t in range(50):
        pressure = 0.03 * t
        N = min(25, max(5, N + pressure))
        rho = min(3.0, max(0.5, rho + 0.02 * pressure))
        latency = min(50, 22 + N * 0.9)
        w.writerow([t, round(N,1), round(rho,2), round(latency,2)])
