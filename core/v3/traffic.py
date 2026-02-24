import csv
def generate_v3_emission_csv():
    # Deterministic traffic: Constant emission rate (Indistinguishable)
    with open('tag_results/v3.0_emission.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["time_index", "packet_emission_rate"])
        for i in range(10):
            writer.writerow([i, 100]) # Fixed 100 pkt/s
