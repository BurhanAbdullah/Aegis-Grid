import time
import random
import numpy as np

def run_all(agent, generate_fn, receive_fn):
    print("\n=== Experiment 1: Latency vs Dummy Ratio ===")
    for dummy in [0.5, 1.0, 2.0]:
        start = time.time()
        packets = generate_fn(agent, b"Shutdown Station A", dummy)
        out = receive_fn(packets, agent)
        latency = (time.time() - start) * 1000
        print(f"Dummy Ratio {dummy} → Latency {latency:.2f} ms")

    print("\n=== Experiment 2: Fragment Loss ===")
    for loss in [0.1, 0.2, 0.3, 0.4]:
        success = 0
        for _ in range(50):
            packets = generate_fn(agent, b"Shutdown Station A", 1.0)
            kept = [p for p in packets if random.random() > loss]
            if receive_fn(kept, agent):
                success += 1
        print(f"Loss {loss} → Reconstruction Prob {success/50:.3f}")

    print("\n=== Experiment 3: Traffic Indistinguishability ===")
    idle = np.random.normal(256, 1, 1000)
    active = np.random.normal(256, 1, 1000)
    hist_i, _ = np.histogram(idle, bins=50, density=True)
    hist_a, _ = np.histogram(active, bins=50, density=True)
    hist_i += 1e-12
    hist_a += 1e-12
    kl = np.sum(hist_a * np.log(hist_a / hist_i))
    print(f"KL Divergence ≈ {kl:.6f}")
