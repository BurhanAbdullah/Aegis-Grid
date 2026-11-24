import csv

# Parameters (model-level, deterministic)
message_sizes = [512, 768, 1024, 1536, 2048]  # bits
base_latency_ms = 10                          # fixed processing
per_bit_latency = 0.015                       # ms per bit

out = "paper_results/2026/csv/v1_latency_feasibility.csv"

with open(out, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["message_bits", "latency_ms"])
    for bits in message_sizes:
        latency = base_latency_ms + bits * per_bit_latency
        writer.writerow([bits, round(latency, 2)])

print("[OK] v1 latency CSV generated")
