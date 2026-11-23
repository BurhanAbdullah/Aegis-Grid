"""Shared experiment utilities: provenance capture and non-overwriting output dirs.

Every runner calls ``start(exp_id, config)`` which
  * creates results/raw/<exp_id>/run_<UTC timestamp>/ (never overwrites),
  * writes config.json and environment.json (commit, dirty flag, versions, CPU),
and returns the run directory.  ``finish`` writes status.json.
"""
import datetime, json, os, platform, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _git(*a):
    try:
        return subprocess.check_output(["git", "-C", ROOT, *a], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _pkg(name):
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return None


def environment():
    cpu = "unknown"
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip(); break
    except OSError:
        pass
    try:
        import ssl
        ossl = ssl.OPENSSL_VERSION
    except Exception:
        ossl = None
    try:
        from cryptography.hazmat.backends.openssl.backend import backend
        crypto_ossl = backend.openssl_version_text()
    except Exception:
        crypto_ossl = None
    return {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain")),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_model": cpu,
        "cpu_count": os.cpu_count(),
        "python_ssl_openssl": ossl,
        "cryptography_openssl": crypto_ossl,
        "packages": {p: _pkg(p) for p in ("cryptography", "numpy", "scipy", "scikit-learn", "pandas",
                                         "matplotlib", "andes")},
        "hardware_class": "virtualised x86-64 cloud VM (not embedded hardware)",
    }


def start(exp_id, config):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = os.environ.get("AEGIS_RESULTS_DIR", os.path.join(ROOT, "results", "raw"))   # smoke runs go elsewhere
    d = os.path.join(base, exp_id, f"run_{ts}")
    os.makedirs(d, exist_ok=False)
    json.dump(config, open(os.path.join(d, "config.json"), "w"), indent=2)
    env = environment(); env["started_utc"] = ts
    json.dump(env, open(os.path.join(d, "environment.json"), "w"), indent=2)
    return d


def finish(run_dir, status="COMPLETED", note=""):
    json.dump({"status": status, "note": note,
               "finished_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")},
              open(os.path.join(run_dir, "status.json"), "w"), indent=2)


def summarize(samples):
    import numpy as np
    a = np.asarray(samples, dtype=float)
    return {"n": int(a.size), "mean": float(a.mean()), "median": float(np.median(a)), "std": float(a.std(ddof=1)) if a.size > 1 else 0.0,
            "p95": float(np.percentile(a, 95)), "p99": float(np.percentile(a, 99)), "min": float(a.min()), "max": float(a.max())}


def load_config(path):
    return json.load(open(path))
