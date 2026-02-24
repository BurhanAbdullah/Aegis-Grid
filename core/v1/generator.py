import csv
# Deterministic Message Sizes for Baseline
message_sizes = [64, 128, 256, 512, 1024]
def generate_v1_results():
    with open('tag_results/v1.0.0.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["message_size", "modeled_latency"])
        for size in message_sizes:
            # Modeled latency: 0.001ms per 64 bytes + base 0.05
            writer.writerow([size, 0.05 + (size/64)*0.001])
