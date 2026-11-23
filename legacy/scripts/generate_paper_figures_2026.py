import pandas as pd
import matplotlib.pyplot as plt
import os

CSV = "paper_results/2026/csv"
OUT = "paper_results/2026/figures"
os.makedirs(OUT, exist_ok=True)

# ---------- Fig 1: v1 Latency ----------
df = pd.read_csv(f"{CSV}/v1_latency_feasibility.csv")
plt.figure()
plt.plot(df.message_bits, df.latency_ms, marker="o")
plt.axhline(50, linestyle="--", color="red")
plt.xlabel("Message Size (bits)")
plt.ylabel("Latency (ms)")
plt.title("Latency Feasibility — Aegis-Grid v1.0.0")
plt.tight_layout()
plt.savefig(f"{OUT}/fig1_v1_latency.png", dpi=300)
plt.close()

# ---------- Fig 2: v2 Reconstruction ----------
df = pd.read_csv(f"{CSV}/v2_reconstruction.csv")
for N in df.N.unique():
    subset = df[df.N == N]
    plt.plot(subset.packet_loss, subset.reconstruction_prob, marker="o", label=f"N={N}")
plt.xlabel("Packet Loss Probability")
plt.ylabel("Reconstruction Probability")
plt.title("Fail-Secure Reconstruction — Aegis-Grid v2.0")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT}/fig2_v2_reconstruction.png", dpi=300)
plt.close()

# ---------- Fig 3: v3 Leakage ----------
df = pd.read_csv(f"{CSV}/v3_information_leakage.csv")
plt.figure()
plt.plot(df.intercepted_fragments, df.mutual_information, marker="o")
plt.xlabel("Intercepted Fragments")
plt.ylabel("Mutual Information")
plt.title("Zero Information Leakage — Aegis-Grid v3.0")
plt.tight_layout()
plt.savefig(f"{OUT}/fig3_v3_leakage.png", dpi=300)
plt.close()

# ---------- Fig 4: v3 Traffic ----------
df = pd.read_csv(f"{CSV}/v3_traffic_entropy.csv")
plt.figure()
plt.plot(df.time, df.active, label="Active")
plt.plot(df.time, df.idle, linestyle="--", label="Idle")
plt.xlabel("Time")
plt.ylabel("Packet Rate")
plt.title("Traffic Indistinguishability — Aegis-Grid v3.0")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT}/fig4_v3_traffic.png", dpi=300)
plt.close()

# ---------- Fig 5: v3 Agent ----------
df = pd.read_csv(f"{CSV}/v3_agent_adaptation.csv")
plt.figure()
plt.plot(df.time, df.N, label="Fragments N")
plt.plot(df.time, df.rho, label="Dummy Ratio ρ")
plt.plot(df.time, df.latency, label="Latency (ms)")
plt.axhline(50, linestyle="--", color="red")
plt.xlabel("Time")
plt.ylabel("Value")
plt.title("Agent Adaptation — Aegis-Grid v3.0-Agentic")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT}/fig5_v3_agent.png", dpi=300)
plt.close()

# ---------- Fig 6: v3 Latency Compare ----------
df = pd.read_csv(f"{CSV}/v3_latency_comparison.csv")
plt.figure()
plt.plot(df.load, df.static, label="Static")
plt.plot(df.load, df.agent, label="Agent")
plt.axhline(50, linestyle="--", color="red")
plt.xlabel("Load")
plt.ylabel("Latency (ms)")
plt.title("Latency: Static vs Agent — Aegis-Grid v3.x")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT}/fig6_v3_latency_compare.png", dpi=300)
plt.close()

# ---------- Fig 7: v4 Safety ----------
df = pd.read_csv(f"{CSV}/v4_control_safety.csv")
plt.figure()
plt.plot(df.time, df.normal, label="Normal")
plt.plot(df.time, df.attack, label="Delayed Attack")
plt.xlabel("Time")
plt.ylabel("Control Action")
plt.title("Fail-Secure Cyber-Physical Safety — Aegis-Grid v4.0")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT}/fig7_v4_safety.png", dpi=300)
plt.close()

print("[OK] All 7 paper figures generated successfully")
