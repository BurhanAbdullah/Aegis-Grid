"""Extract every number quoted in the manuscript from the committed result
directories into results/paper_values.json. The manuscript template refers to
these keys only; no number is typed by hand. Run after all experiments."""
import glob, json, os
import numpy as np, pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def latest(exp, require_clean=False):
    out = []
    for d in sorted(glob.glob(os.path.join(ROOT, "results", "raw", exp, "run_*"))):
        if not os.path.exists(os.path.join(d, "status.json")):
            continue                                  # run in progress
        st = json.load(open(os.path.join(d, "status.json")))
        if st["status"] != "COMPLETED" or "SUPERSEDED" in st.get("note", ""):
            continue
        out.append(d)
    if not out:
        raise SystemExit(f"no usable run for {exp}")
    return out[-1]


def f(x, nd=2):
    return float(round(float(x), nd))


def main():
    V, SRC = {}, {}
    # EXP-002 crypto costs
    r = latest("EXP-002"); SRC["EXP-002"] = r
    s = pd.read_csv(os.path.join(r, "summary_us.csv")).set_index("operation")
    pick = {"mlkem768_encaps": "ML-KEM-768 encaps", "mlkem768_decaps": "ML-KEM-768 decaps", "mlkem768_keygen": "ML-KEM-768 keygen",
            "mlkem1024_encaps": "ML-KEM-1024 encaps", "mlkem1024_decaps": "ML-KEM-1024 decaps",
            "mldsa44_sign": "ML-DSA-44 sign", "mldsa44_verify": "ML-DSA-44 verify", "mldsa65_sign": "ML-DSA-65 sign",
            "mldsa65_verify": "ML-DSA-65 verify", "mldsa87_sign": "ML-DSA-87 sign", "mldsa87_verify": "ML-DSA-87 verify",
            "x25519_exchange": "X25519 exchange", "x509_validate": "X.509 validate (ML-DSA-65 cert)",
            "aesgcm_1k_enc": "AES-256-GCM encrypt 1024B"}
    for k, op in pick.items():
        V[k + "_med_us"] = f(s.loc[op, "median_us"], 1); V[k + "_p99_us"] = f(s.loc[op, "p99_us"], 1)
    for k, name in {"0101": "AGP1_MLKEM768_MLDSA65_AES256GCM_SHA384", "0102": "AGP1_X25519MLKEM768_MLDSA65_AES256GCM_SHA384",
                    "0201": "AGP1_MLKEM1024_MLDSA87_AES256GCM_SHA384", "0301": "AGP1_MLKEM768_MLDSA44_AES256GCM_SHA256"}.items():
        op = f"handshake {name}: total CPU"
        V[f"hs{k}_cpu_med_ms"] = f(s.loc[op, "median_us"] / 1e3); V[f"hs{k}_cpu_p99_ms"] = f(s.loc[op, "p99_us"] / 1e3)
        V[f"seal64_{k}_med_us"] = f(s.loc[f"record seal 64B ({name})", "median_us"], 1)
        V[f"open64_{k}_med_us"] = f(s.loc[f"record open 64B ({name})", "median_us"], 1)
    wb = json.load(open(os.path.join(r, "handshake_wire_bytes.json")))
    V["hs_wire_bytes"] = wb
    for k, name in {"0101": "AGP1_MLKEM768_MLDSA65_AES256GCM_SHA384", "0102": "AGP1_X25519MLKEM768_MLDSA65_AES256GCM_SHA384",
                    "0201": "AGP1_MLKEM1024_MLDSA87_AES256GCM_SHA384", "0301": "AGP1_MLKEM768_MLDSA44_AES256GCM_SHA256"}.items():
        V[f"hs{k}_bytes"] = int(wb[name]["total"])
    # EXP-003 reliability
    r = latest("EXP-003"); SRC["EXP-003"] = r
    d = pd.read_csv(os.path.join(r, "delivery_montecarlo.csv"))
    def P(model, k, n, loss, burst=1):
        x = d[(d.model == model) & (d.k == k) & (d.n == n) & np.isclose(d.mean_loss, loss) & (d.mean_burst == burst)]
        assert len(x) == 1, (model, k, n, loss, burst); return x.iloc[0]
    for k in (5, 10, 20, 30):
        V[f"bern05_k{k}"] = f(P("bernoulli", k, k, 0.05).p_delivery, 3)
        V[f"gil05b5_k{k}"] = f(P("gilbert", k, k, 0.05, 5).p_delivery, 3)
    for k, n in ((5, 7), (5, 8), (10, 15), (20, 28)):
        V[f"bern10_{k}_{n}"] = f(P("bernoulli", k, n, 0.10).p_delivery, 3)
        V[f"gil10b5_{k}_{n}"] = f(P("gilbert", k, n, 0.10, 5).p_delivery, 3)
        V[f"mp10b5_{k}_{n}"] = f(P("gilbert_2path", k, n, 0.10, 5).p_delivery, 3)
    V["trials"] = int(d.trials.iloc[0])
    V["bern10_k5_equiv"] = f(P("bernoulli", 5, 5, 0.10).p_delivery, 3); V["gil10b5_k5_equiv"] = f(P("gilbert", 5, 5, 0.10, 5).p_delivery, 3)
    ab = json.load(open(os.path.join(r, "abstraction_check.json"))); V["abstraction_overlap"] = f"{sum(a['ci_overlap'] for a in ab)}/{len(ab)}"
    ov = pd.read_csv(os.path.join(r, "overhead_and_thresholds.csv"))
    o = ov[(ov.message_bytes == 32)].set_index(["k", "n"])
    V["ov32_single"] = int(o.single_record_bytes.iloc[0]); V["ov32_5_5"] = int(o.loc[(5, 5), "bytes_per_message"])
    V["ov32_20_28"] = int(o.loc[(20, 28), "bytes_per_message"]); V["ov32_5_7"] = int(o.loc[(5, 7), "bytes_per_message"])
    # EXP-004 partial capture
    r = latest("EXP-004"); SRC["EXP-004"] = r
    p = pd.read_csv(os.path.join(r, "partial_capture.csv"))
    leg = p[p.scheme.str.startswith("legacy")].set_index("k"); new = p[~p.scheme.str.startswith("legacy")]
    for k in (5, 10, 20, 30):
        V[f"xor_leak_{k}"] = f(leg.loc[k, "mean_fraction_bytes_recovered"] * 100, 1)
    V["aont_leak_mean_max"] = f(new.mean_fraction_bytes_recovered.max() * 100, 2); V["aont_leak_trial_max"] = f(new["max"].max() * 100, 1)
    # EXP-006 / EXP-011 attacker, EXP-005 latency
    for exp in ("EXP-006", "EXP-011"):
        try:
            r = latest(exp)
        except SystemExit:
            continue
        SRC[exp] = r
        R = pd.read_csv(os.path.join(r, "classifier_test_results.csv"))
        for _, x in R[R.task == "binary"].iterrows():
            key = f"{exp[-3:]}_{x.condition}_{x.model}"
            V[key + "_auc"] = f(x.roc_auc, 3); V[key + "_lo"] = f(x.roc_auc_ci_lo, 3); V[key + "_hi"] = f(x.roc_auc_ci_hi, 3)
            V[key + "_mde"] = f(x.mde_auc_alpha05_power80, 3)
        for _, x in R[R.task == "multiclass"].iterrows():
            V[f"{exp[-3:]}_{x.condition}_{x.model}_mc_auc"] = f(x.roc_auc, 3)
        for c, g in R[R.task == "binary"].groupby("condition"):
            V[f"{exp[-3:]}_{c}_best_auc"] = f(g.roc_auc.max(), 3); V[f"{exp[-3:]}_{c}_best_model"] = g.sort_values("roc_auc").model.iloc[-1]
            V[f"{exp[-3:]}_{c}_auc_range"] = f"{g.roc_auc.min():.2f}–{g.roc_auc.max():.2f}"
            V[f"{exp[-3:]}_{c}_ntest"] = int(g.n_test_windows.iloc[0])
        pm = pd.read_csv(os.path.join(r, "permutation_tests.csv"))
        for _, x in pm.iterrows():
            V[f"{exp[-3:]}_{x.condition}_perm_p"] = f(x.perm_p, 3)
        ks = pd.read_csv(os.path.join(r, "ks_tests.csv"))
        for _, x in ks.iterrows():
            V[f"{exp[-3:]}_{x.condition}_ks_{x.feature.replace(' ', '_')}_p"] = f(x.p_value, 3)
        e = pd.read_csv(os.path.join(r, "effect_sizes.csv")); e["a"] = e.cliffs_delta_active_vs_steady.abs()
        for c, g in e.groupby("condition"):
            t = g.sort_values("a").iloc[-1]; V[f"{exp[-3:]}_{c}_top_feature"] = t.feature; V[f"{exp[-3:]}_{c}_top_delta"] = f(t.cliffs_delta_active_vs_steady, 2)
        bw = pd.read_csv(os.path.join(r, "bandwidth_overhead.csv"))
        for _, x in bw.iterrows():
            V[f"{exp[-3:]}_{x.condition}_bw_ratio"] = f(x.overhead_vs_unshaped, 2) if "unshaped" in set(bw.condition) else None
            V[f"{exp[-3:]}_{x.condition}_kBps"] = f(x.wire_bytes_per_s / 1e3, 1)
        L = pd.read_csv(os.path.join(r, "latency_delivery.csv"))
        for _, x in L.iterrows():
            k = f"{exp[-3:]}_{x.condition}_{x['class']}"
            V[k + "_deliv"] = f(x.delivered_frac, 3); V[k + "_p50"] = f(x.latency_p50_ms, 2); V[k + "_p99"] = f(x.latency_p99_ms, 2)
    # EXP-007 CAP
    r = latest("EXP-007"); SRC["EXP-007"] = r
    S = pd.read_csv(os.path.join(r, "summary.csv"))
    for _, x in S.iterrows():
        k = f"cap_{x.variant}_{x.family}"
        for m in ("detection_rate", "delay_mean", "delivery_under_attack", "false_onsets_per_1000", "mean_n"):
            if pd.notna(x[m]):
                V[f"{k}_{m}"] = f(x[m], 3)
    cal = pd.read_csv(os.path.join(r, "calibration.csv")).set_index("variant")
    for v in cal.index:
        V[f"cap_theta_{v}"] = f(cal.loc[v, "theta"], 2); V[f"cap_calfrac_{v}"] = f(cal.loc[v, "calibration_alarm_fraction"], 4)
    # EXP-008 / EXP-012 AGC
    for exp in ("EXP-008", "EXP-012"):
        try:
            r = latest(exp)
        except SystemExit:
            continue
        SRC[exp] = r
        A = pd.read_csv(os.path.join(r, "summary.csv")); T = pd.read_csv(os.path.join(r, "timeseries.csv.gz"))
        cfg = json.load(open(os.path.join(r, "config.json"))); f0 = cfg["limits_ASSUMPTION"]["f_nominal_hz"]
        for _, x in A.iterrows():
            k = f"{exp[-3:]}_{x.scenario}_{'sec' if x.receiver.startswith('secure') else 'ins'}"
            V[k + "_maxdev"] = f(x.max_abs_dev_hz, 3); V[k + "_fmin_dev"] = f(x.f_min_hz - f0, 3)
            V[k + "_first_viol"] = None if pd.isna(x.first_ss_violation_after_attack_start_s) else f(x.first_ss_violation_after_attack_start_s, 1)
            if "analytic_hold_time_to_band_s" in x and pd.notna(x.analytic_hold_time_to_band_s):
                V[k + "_analytic"] = f(x.analytic_hold_time_to_band_s, 0)
            s = T[(T.scenario == x.scenario) & (T.receiver == x.receiver)]
            a = s[s.attack]
            if len(a):
                V[k + "_min_during"] = f(a.f_hz.min() - f0, 3); V[k + "_max_after"] = f(s[s.t_s > a.t_s.max()].f_hz.max() - f0, 3)
            V[k + "_rejects"] = x.receiver_rejects
    # EXP-009 protocols
    r = latest("EXP-009"); SRC["EXP-009"] = r
    P9 = pd.read_csv(os.path.join(r, "summary.csv"))
    for i, x in P9.iterrows():
        V[f"p9_{i}_name"] = x.configuration
        for m in ("handshake_wall_ms_median", "handshake_wall_ms_p99", "handshake_bytes_total", "oneway_us_median", "oneway_us_p99", "wire_bytes_per_96B_message"):
            V[f"p9_{i}_{m}"] = None if pd.isna(x[m]) else f(x[m], 2)
    # EXP-013 TLS chain-matched
    try:
        r = latest("EXP-013"); SRC["EXP-013"] = r
        for _, x in pd.read_csv(os.path.join(r, "summary.csv")).iterrows():
            k = f"p13_{x.group}_{x.variant}"
            V[k + "_bytes"] = int(x.bytes_total); V[k + "_cpu_med_ms"] = f(x.cpu_us_median / 1e3); V[k + "_cpu_p99_ms"] = f(x.cpu_us_p99 / 1e3)
            V[k + "_chains"] = f"{x.chain_len_server_to_client}/{x.chain_len_client_to_server}"
    except SystemExit:
        pass
    # test counts (collected, not hand-typed)
    import subprocess
    def ntests(path):
        o = subprocess.run(["python3", "-m", "pytest", "-q", "--collect-only", path], cwd=ROOT, capture_output=True, text=True).stdout
        return int([l for l in o.splitlines() if "collected" in l or "tests" in l][-1].split()[0])
    V["n_tests"] = ntests("tests"); V["n_security_tests"] = ntests("tests/security")
    V["_sources"] = {k: os.path.relpath(v, ROOT) for k, v in SRC.items()}
    json.dump(V, open(os.path.join(ROOT, "results", "paper_values.json"), "w"), indent=1, default=str)
    print(len(V), "values;", V["_sources"])


if __name__ == "__main__":
    main()
