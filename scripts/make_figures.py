"""Regenerate every manuscript figure (600 dpi PNG + vector PDF) and its source CSV
from the committed run directories. No number is typed in by hand: each panel
reads results/raw/<EXP>/run_*/ (the run used is printed and written to
figures/FIGURE_SOURCES.csv)."""
import glob, json, os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "figures")
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, MUTED = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e5e1", "grid.linewidth": 0.6, "lines.linewidth": 1.6,
                     "legend.frameon": False, "savefig.dpi": 600, "figure.dpi": 100})
SOURCES = []


def run(exp, prefer=None):
    runs = sorted(d for d in glob.glob(os.path.join(ROOT, "results", "raw", exp, "run_*"))
                  if json.load(open(os.path.join(d, "status.json")))["status"] == "COMPLETED")
    if prefer:
        runs = [r for r in runs if prefer in r] or runs
    if not runs:
        raise SystemExit(f"no completed run for {exp}")
    return runs[-1]


def save(fig, name, df, src):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=600, bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    df.to_csv(os.path.join(OUT, name + ".csv"), index=False)
    plt.close(fig)
    for s in src:
        SOURCES.append({"figure": name, "source_run": os.path.relpath(s, ROOT)})
    print(name, "<-", [os.path.relpath(s, ROOT) for s in src])


def fig_reliability():
    r = run("EXP-003"); d = pd.read_csv(os.path.join(r, "delivery_montecarlo.csv"))
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), sharey=True)
    b = d[d.model == "bernoulli"]
    for i, (k, n) in enumerate([(5, 5), (10, 10), (20, 20), (5, 7), (10, 15), (20, 28)]):
        s = b[(b.k == k) & (b.n == n)].sort_values("mean_loss")
        ax[0].errorbar(s.mean_loss * 100, s.p_delivery, yerr=[s.p_delivery - s.ci95_lo, s.ci95_hi - s.p_delivery],
                       color=C[i % 3], ls="-" if k == n else "--", marker="o" if k == n else "s", ms=3, capsize=0,
                       label=f"k={k}, n={n}")
    ax[0].set_xlabel("Packet loss rate (%)"); ax[0].set_ylabel("P(message delivered)")
    ax[0].set_title("(a) Independent (Bernoulli) loss", fontsize=8, loc="left")
    g = d[(d.model == "gilbert") & (d.mean_burst == 5)]
    for i, (k, n) in enumerate([(5, 5), (10, 10), (20, 20), (5, 7), (10, 15), (20, 28)]):
        s = g[(g.k == k) & (g.n == n)].sort_values("mean_loss")
        ax[1].errorbar(s.mean_loss * 100, s.p_delivery, yerr=[s.p_delivery - s.ci95_lo, s.ci95_hi - s.p_delivery],
                       color=C[i % 3], ls="-" if k == n else "--", marker="o" if k == n else "s", ms=3, capsize=0)
    ax[1].set_xlabel("Mean packet loss rate (%)")
    ax[1].set_title("(b) Gilbert burst loss, mean burst 5 packets", fontsize=8, loc="left")
    fig.tight_layout()
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=6, fontsize=6.5, bbox_to_anchor=(0.5, 0.0))
    save(fig, "Fig3_delivery_vs_loss", pd.concat([b, g]), [r])


def fig_partial_capture():
    r = run("EXP-004"); d = pd.read_csv(os.path.join(r, "partial_capture.csv"))
    d["label"] = d.apply(lambda x: ("XOR (legacy)" if x.scheme.startswith("legacy") else "AONT+RS") + f"\n{x.k}/{x.n}", axis=1)
    fig, ax = plt.subplots(figsize=(3.5, 2.4))
    cols = [C[1] if s.startswith("legacy") else C[0] for s in d.scheme]
    ax.bar(range(len(d)), d.mean_fraction_bytes_recovered * 100, color=cols, width=0.7)
    ax.axhline(100 / 256, color=MUTED, ls=":", lw=1); ax.text(len(d) - 0.5, 100 / 256 + 2, "chance 0.39 %", ha="right", fontsize=6.5, color=MUTED)
    ax.set_xticks(range(len(d))); ax.set_xticklabels(d.label, fontsize=6)
    ax.set_ylabel("Plaintext bytes recovered (%)\nfrom k−1 fragments"); ax.set_ylim(0, 100)
    fig.tight_layout(); save(fig, "Fig4_partial_capture", d.drop(columns="label"), [r])


def fig_protocols():
    r = run("EXP-009", prefer=os.environ.get("EXP009_RUN")); d = pd.read_csv(os.path.join(r, "summary.csv"))
    d2 = d[d.handshake_wall_ms_median.notna()]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
    y = np.arange(len(d2))
    ax[0].barh(y, d2.handshake_wall_ms_median, color=[C[0] if c.startswith("AGP") else C[1] for c in d2.configuration], height=0.6)
    ax[0].errorbar(d2.handshake_wall_ms_p99, y, fmt="|", color=INK, ms=6)
    ax[0].set_yticks(y); ax[0].set_yticklabels([c.replace(", ", "\n", 1) for c in d2.configuration], fontsize=5.5)
    ax[0].invert_yaxis(); ax[0].set_xlabel("Handshake wall time (ms); bar = median, | = p99")
    y = np.arange(len(d))
    ax[1].barh(y, d.oneway_us_median, color=[C[0] if c.startswith("AGP") else (C[2] if c.startswith("IEC") else C[1]) for c in d.configuration], height=0.6)
    ax[1].errorbar(d.oneway_us_p99, y, fmt="|", color=INK, ms=6)
    ax[1].set_yticks(y); ax[1].set_yticklabels([""] * len(d)); ax[1].invert_yaxis()
    ax[1].set_xlabel("One-way latency, 96-byte message (µs)")
    fig.tight_layout(); save(fig, "Fig9_protocol_baselines", d, [r])


def fig_cap():
    r = run("EXP-007"); d = pd.read_csv(os.path.join(r, "summary.csv")); sw = pd.read_csv(os.path.join(r, "theta_sweep_cap.csv"))
    fams = ["A1_burst_jamming", "A2_iid_drop", "A3_delay_injection", "A4_slow_ramp", "A5_pulsed", "A6_injection_flood"]
    short = ["A1 burst", "A2 i.i.d.", "A3 delay", "A4 ramp", "A5 pulsed", "A6 inject"]
    var = ["CAP", "EWMA", "CUSUM", "Shewhart", "static_n=7", "static_n=10"]
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.5))
    w = 0.13
    for i, v in enumerate(var):
        s = d[d.variant == v].set_index("family")
        ax[0].bar(np.arange(6) + (i - 2.5) * w, [s.loc[f, "delivery_under_attack"] for f in fams], w, color=C[i], label=v)
    ax[0].set_xticks(range(6)); ax[0].set_xticklabels(short, rotation=40, fontsize=6); ax[0].set_ylim(0.7, 1.0)
    ax[0].set_ylabel("Delivery during attack"); ax[0].set_title("(a)", loc="left", fontsize=8)
    for i, v in enumerate(var[:4]):
        s = d[d.variant == v].set_index("family")
        ax[1].scatter([s.loc["benign", "false_onsets_per_1000"]], [s.loc["A4_slow_ramp", "delay_mean"]], color=C[i], s=22, zorder=3)
        ax[1].annotate(v, (s.loc["benign", "false_onsets_per_1000"], s.loc["A4_slow_ramp", "delay_mean"]), fontsize=6,
                       xytext=(4, 2), textcoords="offset points")
    ax[1].set_xlabel("False adaptations per 1000 benign epochs"); ax[1].set_ylabel("Mean detection delay,\nslow ramp (epochs)")
    ax[1].set_title("(b)", loc="left", fontsize=8)
    ax[2].plot(sw.theta, sw.false_onsets_per_1000_benign, color=C[0], marker="o", ms=3, label="false adaptations /1000")
    ax[2].set_xscale("log"); ax[2].set_xlabel("CAP threshold θ"); ax[2].set_ylabel("False adaptations per 1000\nbenign epochs")
    cal = pd.read_csv(os.path.join(r, "calibration.csv")).set_index("variant").loc["CAP", "theta"]
    ax[2].axvline(cal, color=MUTED, ls=":", lw=1); ax[2].text(cal * 1.1, ax[2].get_ylim()[1] * 0.8, f"calibrated θ={cal:.2f}", fontsize=6, color=MUTED)
    ax[2].set_title("(c)", loc="left", fontsize=8)
    fig.tight_layout()
    h, l = ax[0].get_legend_handles_labels(); fig.legend(h, l, loc="upper center", ncol=6, fontsize=6.5, bbox_to_anchor=(0.5, 0.0))
    save(fig, "Fig7_cap_vs_baselines", d, [r])


if __name__ == "__main__":
    which = sys.argv[1:] or [n for n in dir() if n.startswith("fig_")]
    for n in which:
        globals()[n]()
    pd.DataFrame(SOURCES).to_csv(os.path.join(OUT, "FIGURE_SOURCES.csv"), index=False)
