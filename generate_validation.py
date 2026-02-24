import time
import matplotlib.pyplot as plt
import numpy as np
import os
from core.crypto.encryption import AegisCrypt
from core.crypto.entropy import shannon_entropy as calculate_entropy

def run_validation():
    key = os.urandom(32)
    engine = AegisCrypt(key)
    
    # 1. Latency Benchmark (Objective 9)
    latencies = []
    for _ in range(1000):
        res = engine.seal(b"GRID_PT_01_ON")
        latencies.append(res['latency'] * 1000000) 
    
    # 2. Entropy Verification (Objective 4 Proof)
    res = engine.seal(b"POWER_GRID_CRITICAL_CMD_001")
    h_cipher = calculate_entropy(res['ciphertext'])
    h_dummy = calculate_entropy(os.urandom(len(res['ciphertext'])))
    
    print(f"\n--- Aegis-Grid Model Validation ---")
    print(f"Mean Agent Latency: {np.mean(latencies):.2f} μs")
    print(f"Cipher Entropy: {h_cipher:.4f} bits/byte")
    print(f"Dummy Entropy:  {h_dummy:.4f} bits/byte")
    print(f"Indistinguishability Delta: {abs(h_cipher - h_dummy):.4f}")

    # Plot Latency Distribution for Paper
    plt.figure(figsize=(10, 4))
    plt.hist(latencies, bins=40, color='#2c3e50', alpha=0.8)
    plt.axvline(np.mean(latencies), color='r', linestyle='dashed', label='Mean Latency')
    plt.title('Aegis-Grid: Computational Overhead (Objective 9)')
    plt.xlabel('Processing Time (Microseconds)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.savefig('plots/latency_analysis.png')
    print("Plot saved to plots/latency_analysis.png")

if __name__ == "__main__":
    run_validation()
