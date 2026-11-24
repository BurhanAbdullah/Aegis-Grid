"""EXP-009 — protocol baselines at matched settings (HARDWARE MEASUREMENT, VM loopback).
Each configuration runs in a fresh interpreter (exp009_worker.py); for TLS the
group is forced through OPENSSL_CONF and verified from the ServerHello."""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pandas as pd
from experiments.common import start, finish, load_config, ROOT
from baselines.tls13 import OPENSSL_CONF_TEMPLATE

WORKER = os.path.join(os.path.dirname(__file__), "exp009_worker.py")


def main(path):
    cfg = load_config(path)
    run = start(cfg["exp_id"], cfg)
    rows, raw = [], []
    for c in cfg["configs"]:
        a = {k: cfg[k] for k in ("handshakes", "messages", "msg_bytes", "gap_ms", "deadline_ms")}
        a.update({k: v for k, v in c.items() if k != "name"})
        env = dict(os.environ)
        with tempfile.TemporaryDirectory() as td:
            a["tmp"] = td
            if c["mode"] == "tls":
                conf = os.path.join(td, "openssl.cnf")
                open(conf, "w").write(OPENSSL_CONF_TEMPLATE.format(groups=c["groups"]))
                env["OPENSSL_CONF"] = conf
            out = subprocess.run([sys.executable, WORKER, json.dumps(a)], env=env, capture_output=True, text=True, timeout=1800)
        if out.returncode != 0:
            raise RuntimeError(out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1]); r["name"] = c["name"]
        if c["mode"] == "tls" and r["group"].lower() != c["groups"].lower():
            raise RuntimeError(f"negotiated {r['group']} != requested {c['groups']}")
        raw.append(r)
        hs = r.get("handshake_wall_us", {})
        rows.append({"configuration": c["name"], "handshake_wall_ms_median": hs.get("median", float("nan")) / 1e3,
                     "handshake_wall_ms_p99": hs.get("p99", float("nan")) / 1e3,
                     "handshake_bytes_total": r.get("handshake_bytes_c2s", 0) + r.get("handshake_bytes_s2c", 0) or None,
                     "oneway_us_median": r["oneway_us"]["median"], "oneway_us_p99": r["oneway_us"]["p99"],
                     "oneway_us_max": r["oneway_us"]["max"], "messages_delivered": r["oneway_us"]["n"],
                     "wire_bytes_per_96B_message": r["wire_bytes_per_message"], "transport": r["transport"]})
        print(rows[-1], flush=True)
    json.dump(raw, open(os.path.join(run, "raw.json"), "w"), indent=1)
    pd.DataFrame(rows).to_csv(os.path.join(run, "summary.csv"), index=False)
    finish(run)
    print(run)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "experiments", "configs", "EXP-009_protocol_baselines.json"))
