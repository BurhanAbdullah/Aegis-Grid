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
    def usable(d):
        p = os.path.join(d, "status.json")
        if not os.path.exists(p):
            return False                                   # run in progress
        st = json.load(open(p))
        return st["status"] == "COMPLETED" and "SUPERSEDED" not in st.get("note", "")
    runs = sorted(d for d in glob.glob(os.path.join(ROOT, "results", "raw", exp, "run_*")) if usable(d))
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
    save(fig, "Fig5_delivery_vs_loss", pd.concat([b, g]), [r])


def fig_partial_capture():
    r = run("EXP-004"); d = pd.read_csv(os.path.join(r, "partial_capture.csv"))
    d["label"] = d.apply(lambda x: ("XOR (legacy)" if x.scheme.startswith("legacy") else "AONT+RS") + f"\n{x.k}/{x.n}", axis=1)
    fig, ax = plt.subplots(figsize=(3.5, 2.4))
    cols = [C[1] if s.startswith("legacy") else C[0] for s in d.scheme]
    ax.bar(range(len(d)), d.mean_fraction_bytes_recovered * 100, color=cols, width=0.7)
    ax.axhline(100 / 256, color=MUTED, ls=":", lw=1); ax.text(len(d) - 0.5, 100 / 256 + 2, "chance 0.39 %", ha="right", fontsize=6.5, color=MUTED)
    ax.set_xticks(range(len(d))); ax.set_xticklabels(d.label, fontsize=6)
    ax.set_ylabel("Plaintext bytes recovered (%)\nfrom k−1 fragments"); ax.set_ylim(0, 100)
    fig.tight_layout(); save(fig, "Fig6_partial_capture", d.drop(columns="label"), [r])


def fig_protocols():
    r = run("EXP-009", prefer=os.environ.get("EXP009_RUN")); d = pd.read_csv(os.path.join(r, "summary.csv"))
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 3.1), sharey=True)
    y = np.arange(len(d))
    col = [C[0] if c.startswith("AGP") else (C[2] if c.startswith("IEC") else C[1]) for c in d.configuration]
    for a in ax:
        a.set_axisbelow(True)
    hs = d.handshake_wall_ms_median
    ax[0].barh(y, hs.fillna(0), color=col, height=0.6)
    ax[0].errorbar(d.handshake_wall_ms_p99, y, fmt="|", color=INK, ms=6)
    for yi, (m, b) in enumerate(zip(hs, d.handshake_bytes_total)):
        ax[0].text((m if pd.notna(m) else 0) + 0.2, yi, f"{b / 1e3:.1f} kB" if pd.notna(b) else "no handshake (pre-shared key)",
                   va="center", fontsize=5.5, color=MUTED)
    ax[0].set_yticks(y); ax[0].set_yticklabels([c.replace(", ", "\n", 1) for c in d.configuration], fontsize=5.5)
    ax[0].invert_yaxis(); ax[0].set_xlabel("Time (ms)")
    ax[0].set_title("(a) handshake time; label = bytes", loc="left", fontsize=7.5)
    ax[1].barh(y, d.oneway_us_median, color=col, height=0.6)
    ax[1].errorbar(d.oneway_us_p99, y, fmt="|", color=INK, ms=6)
    ax[1].set_xlabel("Time (µs)")
    ax[1].set_title("(b) one-way latency, 96-byte message", loc="left", fontsize=7.5)
    fig.tight_layout(); save(fig, "Fig11_protocol_baselines", d, [r])


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
    save(fig, "Fig9_cap_vs_baselines", d, [r])


def fig_traffic():
    r6 = run("EXP-006"); runs = [r6]
    R = pd.read_csv(os.path.join(r6, "classifier_test_results.csv")); R["source"] = "EXP-006"
    ov = pd.read_csv(os.path.join(r6, "bandwidth_overhead.csv"))
    try:
        r11 = run("EXP-011"); R11 = pd.read_csv(os.path.join(r11, "classifier_test_results.csv")); R11["source"] = "EXP-011"
        R11 = R11[R11.condition.str.endswith("decoupled") | (R11.condition == "shaped_2ms")]
        R11["condition"] = R11.condition.where(R11.condition != "shaped_2ms", "shaped_2ms (repeat)")
        R = pd.concat([R, R11]); runs.append(r11)
    except SystemExit:
        pass
    B = R[R.task == "binary"]
    conds = list(dict.fromkeys(B.condition))
    models = ["logreg", "knn", "random_forest", "hist_gbdt"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7), gridspec_kw={"width_ratios": [2.2, 1]})
    w = 0.2
    for i, m in enumerate(models):
        s = B[B.model == m].set_index("condition").reindex(conds)
        ax[0].errorbar(np.arange(len(conds)) + (i - 1.5) * w, s.roc_auc, yerr=[s.roc_auc - s.roc_auc_ci_lo, s.roc_auc_ci_hi - s.roc_auc],
                       fmt="o", ms=3.5, color=C[i], label=m.replace("_", " "), elinewidth=1)
    ax[0].axhline(0.5, color=MUTED, ls=":", lw=1); ax[0].text(-0.4, 0.51, "chance", fontsize=6, color=MUTED, ha="left")
    lab = {"unshaped": "unshaped", "padded": "padded", "shaped_2ms": "shaped\n2 ms", "shaped_1ms": "shaped\n1 ms",
           "shaped_2ms (repeat)": "shaped 2 ms\nrepeat*", "shaped_2ms_decoupled": "decoupled\n2 ms*", "shaped_1ms_decoupled": "decoupled\n1 ms*"}
    ax[0].set_xticks(range(len(conds))); ax[0].set_xticklabels([lab.get(c, c) for c in conds], fontsize=6.0)
    if len(runs) > 1:
        ax[0].text(0.99, -0.22, "* EXP-011 (new sessions)", transform=ax[0].transAxes, ha="right", fontsize=5.5, color=MUTED)
    ax[0].set_ylim(0.4, 1.02); ax[0].set_ylabel("Test ROC-AUC (steady vs active)\n95 % session-bootstrap CI")
    ax[0].legend(fontsize=6.3, ncol=2, loc="upper right"); ax[0].set_title("(a)", loc="left", fontsize=8); ax[1].set_axisbelow(True)
    o = ov.set_index("condition").reindex(["unshaped", "padded", "shaped_2ms", "shaped_1ms"])
    ax[1].bar(range(4), o.wire_bytes_per_s / 1e3, color=[C[1], C[1], C[0], C[0]], width=0.6)
    ax[1].set_xticks(range(4)); ax[1].set_xticklabels(["unshaped", "padded", "shaped\n2 ms", "shaped\n1 ms"], fontsize=6.3)
    ax[1].set_ylabel("Wire throughput (kB/s)"); ax[1].set_title("(b)", loc="left", fontsize=8)
    for i, v in enumerate(o.overhead_vs_unshaped):
        ax[1].text(i, o.wire_bytes_per_s.iloc[i] / 1e3 + 2, f"×{v:.2f}", ha="center", fontsize=6)
    fig.tight_layout(); save(fig, "Fig7_traffic_attacker", R, runs)


def fig_latency():
    r = run("EXP-005"); m = pd.read_csv(os.path.join(r, "messages.csv.gz"))
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.4), sharey=True)
    conds = ["unshaped", "padded", "shaped_2ms", "shaped_1ms"]
    for j, cl in enumerate(["event", "command", "telemetry"]):
        for i, c in enumerate(conds):
            x = np.sort(m[(m["class"] == cl) & (m.condition == c) & m.delivered].latency_ms.values)
            n = ((m["class"] == cl) & (m.condition == c)).sum()
            ax[j].step(x, np.arange(1, len(x) + 1) / n, where="post", color=C[i], label=c.replace("_", " "))
        dl = m[m["class"] == cl].deadline_ms.iloc[0]
        ax[j].axvline(dl, color=MUTED, ls=":", lw=1); ax[j].set_xscale("log")
        ax[j].set_title(f"({'abc'[j]}) {cl}, deadline {dl:g} ms", loc="left", fontsize=7.5)
        ax[j].set_xlabel("End-to-end latency (ms)")
    ax[0].set_ylabel("Fraction of messages\ndelivered by latency")
    fig.tight_layout(); h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=4, fontsize=6.5, bbox_to_anchor=(0.5, 0.0))
    summ = m.groupby(["condition", "class"]).agg(delivered=("delivered", "mean"), p50=("latency_ms", "median"),
                                                 p99=("latency_ms", lambda x: x.quantile(.99))).reset_index()
    save(fig, "Fig8_latency_by_class", summ, [r])


def fig_agc():
    r = run("EXP-008"); t = pd.read_csv(os.path.join(r, "timeseries.csv.gz")); cfg = json.load(open(os.path.join(r, "config.json")))
    f0 = cfg["limits_ASSUMPTION"]["f_nominal_hz"]; band = cfg["limits_ASSUMPTION"]["steady_state_band_hz"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), sharey=False)
    for i, sc in enumerate(["no_attack", "drop_60s", "drop_120s", "drop_240s"]):
        s = t[(t.scenario == sc) & (t.receiver == "secure_failsecure")]
        ax[0].plot(s.t_s, s.f_hz - f0, color=C[i], label=sc.replace("_", " "))
    a0 = cfg["attack_start_s"]
    try:                                                   # EXP-012: same 240 s outage with anti-windup
        r12 = run("EXP-012"); t12 = pd.read_csv(os.path.join(r12, "timeseries.csv.gz"))
        s = t12[(t12.scenario == "drop_240s") & (t12.receiver == "secure_failsecure")]
        ax[0].plot(s.t_s, s.f_hz - f0, color=C[3], ls="--", label="drop 240s, anti-windup (EXP-012)")
    except SystemExit:
        r12 = None
    ax[0].axvspan(a0, a0 + 240, color="#f3f2ee", zorder=0)
    for y in (-band, band):
        ax[0].axhline(y, color=MUTED, ls=":", lw=1)
    ax[0].set_xlabel("Time (s)"); ax[0].set_ylabel("Frequency deviation (Hz)")
    ax[0].set_title("(a) AGC commands dropped; U_safe = hold", loc="left", fontsize=7.5); ax[0].legend(fontsize=6.3)
    for i, (sc, rc, lab) in enumerate([("forge_60s", "insecure_accept_all", "forged, unauthenticated"),
                                       ("forge_60s", "secure_failsecure", "forged, AGP/1 fail-secure"),
                                       ("replay_60s", "insecure_accept_all", "replayed, unauthenticated"),
                                       ("delay_10s_60s", "insecure_accept_all", "10 s stale, unauthenticated")]):
        s = t[(t.scenario == sc) & (t.receiver == rc)]
        ax[1].plot(s.t_s, s.f_hz - f0, color=C[[1, 0, 2, 3][i]], label=lab)
    ax[1].axvspan(a0, a0 + 60, color="#f3f2ee", zorder=0)
    for y in (-band, band):
        ax[1].axhline(y, color=MUTED, ls=":", lw=1)
    ax[1].set_xlabel("Time (s)"); ax[1].set_title("(b) forged / replayed / delayed commands", loc="left", fontsize=7.5)
    ax[1].legend(fontsize=6.3)
    fig.tight_layout()
    save(fig, "Fig10_agc_ieee14", pd.read_csv(os.path.join(r, "summary.csv")), [r] + ([r12] if r12 else []))


if __name__ == "__main__":
    which = sys.argv[1:] or [n for n in dir() if n.startswith("fig_")]
    for n in which:
        globals()[n]()
    pd.DataFrame(SOURCES).to_csv(os.path.join(OUT, "FIGURE_SOURCES.csv"), index=False)
