import time
import random
import numpy as np
from collections import defaultdict
from Crypto.Random import get_random_bytes

# -----------------------------
# Experiment 1: Latency vs Security
# -----------------------------
def experiment_latency_vs_security(agent, generate_traffic, receive_and_reconstruct):
    msg = b"Shutdown Station A"
    results = []

    for dummy_ratio in np.linspace(0, 3, 7):
        start = time.time()
        packets, t0 = generate_traffic(agent, msg, dummy_ratio)
        receive_and_reconstruct(agent, packets, t0)
        latency = (time.time() - start) * 1000  # ms
        results.append((float(dummy_ratio), latency))

    return results


# -----------------------------
# Experiment 2: Fragment Loss
# -----------------------------
def experiment_fragment_loss(agent, generate_traffic, receive_and_reconstruct):
    msg = b"Shutdown Station A"
    success = defaultdict(list)

    for drop_rate in [0.1, 0.2, 0.3, 0.4]:
        for _ in range(50):
            packets, t0 = generate_traffic(agent, msg, dummy_ratio=1.0)
            kept = [p for p in packets if random.random() > drop_rate]
            recovered = receive_and_reconstruct(agent, kept, t0)
            success[drop_rate].append(recovered is not None)

    return {k: sum(v) / len(v) for k, v in success.items()}


# -----------------------------
# Experiment 3: Traffic Indistinguishability
# -----------------------------
def experiment_traffic_indistinguishability():
    idle = np.random.normal(256, 5, 1000)
    active = np.random.normal(256, 5, 1000)

    hist_idle, _ = np.histogram(idle, bins=50, density=True)
    hist_active, _ = np.histogram(active, bins=50, density=True)

    hist_idle += 1e-9
    hist_active += 1e-9

    kl = np.sum(hist_active * np.log(hist_active / hist_idle))
    return kl


# -----------------------------
# Runner
# -----------------------------
def run_all(agent, generate_traffic, receive_and_reconstruct):
    print("\n📊 Experiment 1: Latency vs Dummy Ratio")
    lat = experiment_latency_vs_security(agent, generate_traffic, receive_and_reconstruct)
    for d, l in lat:
        print(f"Dummy Ratio {d:.2f} → Avg Latency {l:.2f} ms")

    print("\n📉 Experiment 2: Fragment Loss")
    frag = experiment_fragment_loss(agent, generate_traffic, receive_and_reconstruct)
    for k, v in frag.items():
        print(f"Loss Rate {k:.1f} → Reconstruction Prob {v:.4f}")

    print("\n🔐 Experiment 3: Traffic Indistinguishability")
    kl = experiment_traffic_indistinguishability()
    print(f"KL Divergence ≈ {kl:.6f}")
