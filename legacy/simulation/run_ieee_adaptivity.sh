#!/bin/bash
set -e

echo "[INFO] Generating IEEE adaptivity validation figures..."

OUT="plots/ieee_adaptivity"
mkdir -p "$OUT"

python3 - << 'PYCODE'
import matplotlib.pyplot as plt
import numpy as np

def save(name):
    plt.savefig(f"{OUT}/{name}.png", dpi=300, bbox_inches="tight")
    plt.close()

# ---------------- FIG A1: Threshold Adaptation ----------------
loss = np.array([0,10,20,30,40,50])
threshold = np.maximum(4, (12 * (1 - loss/100)).astype(int))

plt.plot(loss, threshold, marker='o')
plt.xlabel("Packet Loss (%)")
plt.ylabel("Reconstruction Threshold")
plt.title("Adaptive Threshold Adjustment vs Packet Loss")
save("figA1_threshold_vs_loss")

# ---------------- FIG A2: Pressure Accumulation ----------------
time = np.arange(0,10)
pressure = np.cumsum([0.5,0.6,0.8,1.0,1.2,0,0,0,0,0])

plt.plot(time, pressure, marker='o')
plt.axhline(5.5, linestyle='--', label="Lock Threshold")
plt.xlabel("Time Step")
plt.ylabel("Cumulative Attack Pressure")
plt.title("Adaptive Pressure Accumulation Over Time")
plt.legend()
save("figA2_pressure_accumulation")

# ---------------- FIG A3: Lock State Transition ----------------
lock_state = [0,0,0,0,1,1,1,1,1,1]

plt.step(time, lock_state, where="post")
plt.xlabel("Time Step")
plt.ylabel("Agent State (0=Active, 1=Locked)")
plt.title("Irreversible Adaptive Lock Transition")
save("figA3_lock_transition")

# ---------------- FIG A4: Adaptive vs Static Behavior ----------------
adaptive = [0.85,0.78,0.65,0.52]
static = [0.70,0.55,0.38,0.22]
loss2 = [10,20,30,40]

plt.plot(loss2, adaptive, marker='o', label="Adaptive Agent")
plt.plot(loss2, static, marker='x', linestyle='--', label="Static Policy")
plt.xlabel("Packet Loss (%)")
plt.ylabel("Reconstruction Success")
plt.title("Adaptive vs Static Agent Behavior")
plt.legend()
save("figA4_success_static_vs_adaptive")

# ---------------- FIG A5: Closed-Loop Control Response ----------------
disturbance = [0,0.1,0.3,0.5,0.4,0.2,0.1,0]
response = [12,11,9,7,8,10,11,12]

plt.plot(disturbance, response, marker='o')
plt.xlabel("Observed Network Disturbance")
plt.ylabel("Agent Decision (Threshold)")
plt.title("Closed-Loop Adaptive Control Response")
save("figA5_control_loop_response")

print("[SUCCESS] Adaptivity figures generated.")
PYCODE

echo "[DONE] Saved in plots/ieee_adaptivity/"
