import csv
from core.v2.reconstruct import generate_v2_csv

# Testing 0% to 5% loss
loss_values = [0.0, 0.01, 0.02, 0.05]
n_fragments = 10

with open('tag_results/v2.0.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["packet_loss", "fragment_count", "reconstruction_success"])
    for loss in loss_values:
        writer.writerow(generate_v2_csv(loss, n_fragments))
