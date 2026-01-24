import pandas as pd
import matplotlib.pyplot as plt
import os

CSV = "paper_results/2026/csv"
OUT = "paper_results/2026/figures"
os.makedirs(OUT, exist_ok=True)

def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"{OUT}/{name}", dpi=300)
    plt.close()

# Fig 1
df = pd.read_csv(f"{CSV}/v1_latency_feasibility.csv")
fig = plt.figure()
plt.plot(df.message_bits, df.latency_ms, marker="o")
plt.axhline(50, linestyle="--", color="red")
plt.title("Latency Feasibility — v1.0.0")
plt.xlabel("Message size (bits)")
plt.ylabel("Latency (ms)")
save(fig, "fig1_v1_latency.png")

# Fig 2
df = pd.read_csv(f"{CSV}/v2_reconstruction.csv")
fig = plt.figure()
for N in df.N.unique():
    sub = df[df.N == N]
    plt.plot(sub.packet_loss, sub.success_probability, marker="o", label=f"N={N}")
plt.legend()
plt.title("Fail-Secure Reconstruction — v2.0")
plt.xlabel("Packet loss")
plt.ylabel("Success probability")
save(fig, "fig2_v2_reconstruction.png")

# Fig 3
df = pd.read_csv(f"{CSV}/v3_information_leakage.csv")
fig = plt.figure()
plt.plot(df.intercepted_fragments, df.mutual_information)
plt.title("Bounded Information Leakage — v3")
plt.xlabel("Intercepted fragments")
plt.ylabel("Mutual information")
save(fig, "fig3_v3_leakage.png")

# Fig 4
df = pd.read_csv(f"{CSV}/v3_traffic_entropy.csv")
fig = plt.figure()
plt.plot(df.time, df.active, label="Active")
plt.plot(df.time, df.idle, label="Idle")
plt.legend()
plt.title("Traffic Indistinguishability — v3")
save(fig, "fig4_v3_traffic.png")

# Fig 5
df = pd.read_csv(f"{CSV}/v3_agent_adaptation.csv")
fig = plt.figure()
plt.plot(df.time, df.N, label="N(t)")
plt.plot(df.time, df.latency, label="Latency")
plt.axhline(50, linestyle="--", color="red")
plt.legend()
plt.title("Agent Adaptation — v3")
save(fig, "fig5_v3_agent.png")

# Fig 6
fig = plt.figure()
plt.plot(df.time, df.latency)
plt.axhline(50, linestyle="--", color="red")
plt.title("Latency Bound Preservation — v3")
save(fig, "fig6_v3_latency_compare.png")

# Fig 7
df = pd.read_csv(f"{CSV}/v4_control_safety.csv")
fig = plt.figure()
plt.plot(df.time, df.state_normal, label="Normal")
plt.plot(df.time, df.state_under_attack, label="Attack")
plt.legend()
plt.title("Fail-Secure Control — v4")
save(fig, "fig7_v4_safety.png")

print("[OK] All upgraded paper figures generated")
