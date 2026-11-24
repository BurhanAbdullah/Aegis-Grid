"""EXP-006 — multivariate passive traffic-analysis attacker (SIMULATION RESULT on
HARDWARE-MEASURED traces from EXP-005).

Per 250 ms window the attacker extracts size, count and inter-arrival-time (IAT)
features and predicts the window's activity class. Sessions are split
train/validation/test *before* any fitting; hyper-parameters are chosen on the
validation sessions only, the chosen model is refitted on train+validation and
evaluated once on the held-out test sessions. Uncertainty: cluster bootstrap
over test sessions. Significance: label-permutation test. Power: minimum
detectable AUC (Hanley–McNeil, α=0.05 one-sided, power 0.8).
"""
import glob, itertools, json, os, sys, warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np, pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (roc_auc_score, average_precision_score, accuracy_score,
                             precision_recall_fscore_support)
from experiments.common import start, finish, load_config, ROOT

warnings.filterwarnings("ignore")
WIN = 250.0


def features(g, nwin):
    t, b = g.t_ms.values, g.bytes.values
    rows = []
    edges = np.searchsorted(t, np.arange(nwin + 1) * WIN)
    for w in range(nwin):
        tt, bb = t[edges[w]:edges[w + 1]] - w * WIN, b[edges[w]:edges[w + 1]]
        f = {"n_pkts": len(tt), "bytes": bb.sum(), "size_mean": bb.mean() if len(bb) else 0,
             "size_std": bb.std() if len(bb) else 0, "size_distinct": len(np.unique(bb)),
             "size_max": bb.max() if len(bb) else 0}
        iat = np.diff(tt) if len(tt) > 1 else np.array([WIN])
        for q in (0, 10, 50, 90, 100):
            f[f"iat_p{q}"] = np.percentile(iat, q)
        f["iat_mean"], f["iat_std"] = iat.mean(), iat.std()
        f["iat_cv"] = iat.std() / iat.mean() if iat.mean() > 0 else 0
        sub = np.histogram(tt, bins=10, range=(0, WIN))[0]
        for i, c in enumerate(sub):
            f[f"cnt_bin{i}"] = c
        f["max_cnt_5ms"] = np.histogram(tt, bins=50, range=(0, WIN))[0].max() if len(tt) else 0
        h = np.histogram(np.log10(np.clip(iat, 1e-4, None)), bins=8, range=(-4, 2.5))[0]
        for i, c in enumerate(h):
            f[f"logiat_h{i}"] = c / max(1, len(iat))
        rows.append(f)
    return rows


def model_grid(cfg, seed):
    m = cfg["models"]
    for C in m["logreg"]["C"]:
        yield "logreg", {"C": C}, lambda C=C: make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=5000))
    for k in m["knn"]["n_neighbors"]:
        yield "knn", {"n_neighbors": k}, lambda k=k: make_pipeline(StandardScaler(), KNeighborsClassifier(k))
    for d in m["random_forest"]["max_depth"]:
        yield "random_forest", {"max_depth": d}, lambda d=d: RandomForestClassifier(300, max_depth=d, random_state=seed, n_jobs=2)
    for lr, ln in itertools.product(m["hist_gbdt"]["learning_rate"], m["hist_gbdt"]["max_leaf_nodes"]):
        yield "hist_gbdt", {"learning_rate": lr, "max_leaf_nodes": ln}, \
            lambda lr=lr, ln=ln: HistGradientBoostingClassifier(learning_rate=lr, max_leaf_nodes=ln, random_state=seed)


def auc_task(y, p, task):
    if task == "binary":
        return roc_auc_score(y, p[:, 1])
    return roc_auc_score(y, p, multi_class="ovr", average="macro")


def metrics(y, p, task):
    pred = p.argmax(1)
    avg = "binary" if task == "binary" else "macro"
    pr, rc, f1, _ = precision_recall_fscore_support(y, pred, average=avg, zero_division=0)
    if task == "binary":
        pra = average_precision_score(y, p[:, 1])
    else:
        pra = np.mean([average_precision_score(y == c, p[:, c]) for c in range(p.shape[1])])
    return {"roc_auc": auc_task(y, p, task), "pr_auc": pra, "accuracy": accuracy_score(y, pred),
            "precision": pr, "recall": rc, "f1": f1}


def hanley_se(A, n1, n0):
    q1, q2 = A / (2 - A), 2 * A * A / (1 + A)
    return np.sqrt((A * (1 - A) + (n1 - 1) * (q1 - A * A) + (n0 - 1) * (q2 - A * A)) / (n1 * n0))


def mde_auc(n1, n0, alpha=0.05, power=0.8):
    za, zb = stats.norm.ppf(1 - alpha), stats.norm.ppf(power)
    for A in np.arange(0.5005, 1.0, 0.0005):
        if A - 0.5 >= za * hanley_se(0.5, n1, n0) + zb * hanley_se(A, n1, n0):
            return float(A)
    return 1.0


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    gt = (a[:, None] > b[None, :]).sum(); lt = (a[:, None] < b[None, :]).sum()
    return (gt - lt) / (len(a) * len(b))


def main(path):
    cfg = load_config(path)
    src = cfg["input_run"]
    if src.startswith("LATEST:"):
        base = os.environ.get("AEGIS_RESULTS_DIR", os.path.join(ROOT, "results", "raw"))
        done = [d for d in sorted(glob.glob(os.path.join(base, src[7:], "run_*")))
                if os.path.exists(os.path.join(d, "status.json"))
                and json.load(open(os.path.join(d, "status.json")))["status"] == "COMPLETED"]
        src = done[-1]                      # latest COMPLETED run (in-progress and failed runs skipped)
    cfg["input_run_resolved"] = os.path.relpath(src, ROOT)
    run = start(cfg["exp_id"], cfg)
    rng = np.random.default_rng(cfg["seed"])
    cap = json.load(open(os.path.join(src, "config.json")))
    nwin = int(cap["session_s"] * 1000 / WIN)
    tr = pd.read_csv(os.path.join(src, "traces.csv.gz"))
    labs = pd.read_csv(os.path.join(src, "window_labels.csv"))
    msgs = pd.read_csv(os.path.join(src, "messages.csv.gz"))
    summ = json.load(open(os.path.join(src, "session_summary.json")))
    feats = []
    for (s, c), g in tr.groupby(["session", "condition"]):
        g = g.sort_values("t_ms")
        for w, f in enumerate(features(g, nwin)):
            f.update(session=s, condition=c, window=w); feats.append(f)
    F = pd.DataFrame(feats).merge(labs, on=["session", "window"])
    F.to_csv(os.path.join(run, "features.csv.gz"), index=False)
    fcols = [c for c in F.columns if c not in ("session", "condition", "window", "label")]
    sp = cfg["split_sessions"]
    part = lambda df, k: df[(df.session >= sp[k][0]) & (df.session < sp[k][1])]
    res, sel, perm, eff, ks = [], [], [], [], []
    for cond in cap["conditions"]:
        D = F[F.condition == cond]
        for task in ("multiclass", "binary"):
            y_of = (lambda d: d.label.values) if task == "multiclass" else (lambda d: (d.label.values > 0).astype(int))
            tr_, va, te = part(D, "train"), part(D, "validation"), part(D, "test")
            best = None
            for name, hp, mk in model_grid(cfg, cfg["seed"]):
                m = mk().fit(tr_[fcols].values, y_of(tr_))
                a = auc_task(y_of(va), m.predict_proba(va[fcols].values), task)
                sel.append({"condition": cond, "task": task, "model": name, "hyper": json.dumps(hp), "val_auc": a})
                if best is None or a > best[0]:
                    best = (a, name, hp, mk)
            trva = pd.concat([tr_, va])
            # per family: best hyper-parameters on validation, then single test evaluation
            fam = pd.DataFrame([r for r in sel if r["condition"] == cond and r["task"] == task])
            for name in fam.model.unique():
                hp = json.loads(fam[fam.model == name].sort_values("val_auc").iloc[-1].hyper)
                mk = next(mk for n, h, mk in model_grid(cfg, cfg["seed"]) if n == name and h == hp)
                m = mk().fit(trva[fcols].values, y_of(trva))
                p, y = m.predict_proba(te[fcols].values), y_of(te)
                met = metrics(y, p, task)
                sess = te.session.values; us = np.unique(sess)
                boots = []
                for _ in range(cfg["bootstrap"]):
                    pick = rng.choice(us, len(us))
                    idx = np.concatenate([np.flatnonzero(sess == u) for u in pick])
                    if len(np.unique(y[idx])) < (2 if task == "binary" else 3):
                        continue
                    boots.append(auc_task(y[idx], p[idx], task))
                lo, hi = np.percentile(boots, [2.5, 97.5])
                row = {"condition": cond, "task": task, "model": name, "hyper": json.dumps(hp),
                       "selected_overall": name == best[1], "n_test_windows": len(y), **met,
                       "roc_auc_ci_lo": lo, "roc_auc_ci_hi": hi}
                if task == "binary":
                    n1, n0 = int(y.sum()), int((1 - y).sum())
                    row["mde_auc_alpha05_power80"] = mde_auc(n1, n0)
                    if name == best[1]:
                        obs = met["roc_auc"]
                        null = [roc_auc_score(rng.permutation(y), p[:, 1]) for _ in range(cfg["permutations"])]
                        pv = (1 + sum(v >= obs for v in null)) / (1 + len(null))
                        perm.append({"condition": cond, "model": name, "test_auc": obs, "perm_p": pv,
                                     "null_mean": float(np.mean(null)), "null_p97_5": float(np.percentile(null, 97.5))})
                res.append(row)
        yb = (D.label.values > 0)
        for c in fcols:
            eff.append({"condition": cond, "feature": c, "cliffs_delta_active_vs_steady":
                        cliffs_delta(D[c].values[yb], D[c].values[~yb])})
        for c in ("n_pkts", "iat_mean", "bytes"):
            r = stats.ks_2samp(D[c].values[D.label.values == 0], D[c].values[D.label.values == 1])
            ks.append({"condition": cond, "feature": c, "comparison": "steady vs event",
                       "ks_stat": r.statistic, "p_value": r.pvalue})
        g = tr[tr.condition == cond]
        ks_iat = []
        for s, gg in g.groupby("session"):
            gg = gg.sort_values("t_ms"); iat = np.diff(gg.t_ms.values)
            wi = (gg.t_ms.values[1:] // WIN).astype(int)
            lab = labs[labs.session == s].set_index("window").label.reindex(wi).values
            ks_iat.append((iat[lab == 0], iat[lab == 1]))
        a = np.concatenate([x[0] for x in ks_iat]); b = np.concatenate([x[1] for x in ks_iat])
        r = stats.ks_2samp(a, b)
        ks.append({"condition": cond, "feature": "pooled per-packet IAT", "comparison": "steady vs event windows",
                   "ks_stat": r.statistic, "p_value": r.pvalue})
    pd.DataFrame(res).to_csv(os.path.join(run, "classifier_test_results.csv"), index=False)
    pd.DataFrame(sel).to_csv(os.path.join(run, "model_selection_validation.csv"), index=False)
    pd.DataFrame(perm).to_csv(os.path.join(run, "permutation_tests.csv"), index=False)
    pd.DataFrame(eff).to_csv(os.path.join(run, "effect_sizes.csv"), index=False)
    pd.DataFrame(ks).to_csv(os.path.join(run, "ks_tests.csv"), index=False)
    # bandwidth overhead (UDP payload + 28 B IPv4/UDP header) and latency / deadline
    S = pd.DataFrame(summ)
    dur = cap["session_s"]
    ov = S.groupby("condition").agg(datagrams=("datagrams", "sum"), payload_bytes=("bytes", "sum"),
                                    sessions=("session", "nunique")).reset_index()
    ov["datagrams_per_s"] = ov.datagrams / (ov.sessions * dur)
    ov["wire_bytes_per_s"] = (ov.payload_bytes + 28 * ov.datagrams) / (ov.sessions * dur)
    # EXP-011 input (EXP-010) has no unshaped condition: the ratio is then left empty (NaN)
    base = ov[ov.condition == "unshaped"].wire_bytes_per_s
    ov["overhead_vs_unshaped"] = ov.wire_bytes_per_s / float(base.iloc[0]) if len(base) else np.nan
    ov["note"] = "shaped conditions include a drain period of %g ms after each session" % cap["drain_ms"]
    ov.to_csv(os.path.join(run, "bandwidth_overhead.csv"), index=False)
    L = msgs.groupby(["condition", "class"]).agg(
        messages=("msg_id", "size"), delivered_frac=("delivered", "mean"),
        latency_p50_ms=("latency_ms", "median"), latency_p95_ms=("latency_ms", lambda x: x.quantile(.95)),
        latency_p99_ms=("latency_ms", lambda x: x.quantile(.99)), latency_max_ms=("latency_ms", "max"),
        deadline_ms=("deadline_ms", "first")).reset_index()
    L.to_csv(os.path.join(run, "latency_delivery.csv"), index=False)
    finish(run)
    print(run)
    R = pd.DataFrame(res)
    print(R[["condition", "task", "model", "roc_auc", "roc_auc_ci_lo", "roc_auc_ci_hi", "accuracy", "f1"]].round(3).to_string())
    print(pd.DataFrame(perm).round(4).to_string()); print(ov.round(2).to_string()); print(L.round(3).to_string())
    print(pd.DataFrame(ks).round(4).to_string())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "experiments", "configs", "EXP-006_traffic_attacker.json"))
