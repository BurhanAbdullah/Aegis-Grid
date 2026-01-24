import csv

packet_loss = [0.0, 0.05, 0.1, 0.2, 0.3, 0.4]
Ns = [5, 10, 20]

out = "paper_results/2026/csv/v2_reconstruction.csv"

with open(out, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["packet_loss", "N", "reconstruction_prob"])
    for N in Ns:
        for p in packet_loss:
            # Fail-secure: any loss → zero reconstruction
            prob = 1.0 if p == 0.0 else 0.0
            writer.writerow([p, N, prob])

print("[OK] v2 reconstruction CSV generated")
