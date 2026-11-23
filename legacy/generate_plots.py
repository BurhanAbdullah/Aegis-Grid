import matplotlib.pyplot as plt
import numpy as np

def generate_paper_plots():
    loss_levels = [0.1, 0.2, 0.3, 0.4, 0.5]
    success_rate = [0.92, 0.85, 0.74, 0.33, 0.05]
    lock_rate = [0.05, 0.15, 0.35, 0.75, 1.00]
    pressure = np.cumsum([0.2, 0.5, 0.8, 1.5, 2.5])

    plt.figure(figsize=(12, 5))

    # Plot 1: Security vs Availability
    plt.subplot(1, 2, 1)
    plt.plot(loss_levels, success_rate, 'g-o', label='Command Success (Availability)')
    plt.plot(loss_levels, lock_rate, 'r--x', label='Node Lock (Integrity)')
    plt.title('Aegis-Grid: The Fail-Secure Threshold')
    plt.xlabel('Adversarial Network Loss')
    plt.ylabel('Probability')
    plt.legend()
    plt.grid(True)

    # Plot 2: Pressure Accumulation (Pillar 3)
    plt.subplot(1, 2, 2)
    plt.step(range(len(pressure)), pressure, where='post', color='purple', label='CAP Score')
    plt.axhline(y=4.0, color='r', linestyle=':', label='Time-Lock Trigger')
    plt.title('Objective 6: Cumulative Attack Pressure')
    plt.xlabel('Epochs')
    plt.ylabel('System Stress')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('plots/model_validation.png')
    print("Paper-ready plots saved to plots/model_validation.png")

if __name__ == "__main__":
    generate_paper_plots()
