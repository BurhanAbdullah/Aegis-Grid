"""EXP-013 — TLS 1.3 mutual-authentication handshakes with default (CA included by
OpenSSL auto-chaining) and leaf-only certificate chains, measured in memory.

Each key-exchange group runs in a child process because the group can only be set
through OPENSSL_CONF (Python 3.13 has no set_groups); the negotiated group is
verified from the ServerHello. Label: HARDWARE MEASUREMENT on a virtualised x86-64 VM.

Run: python3 experiments/runners/exp013_tls_chain_matched.py [config]
"""
import csv, gc, json, os, ssl, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from experiments.common import start, finish, summarize, load_config, ROOT


def child(cfg, group, out):
    from baselines import tls13
    d = tempfile.mkdtemp()
    ca, crt, key = tls13.make_pki(d, cfg["sig"])
    rows = []
    for v in cfg["variants"]:
        leaf = v == "mutual_leaf_only"
        times, last = [], None
        for i in range(cfg["warmup"] + cfg["handshakes"]):
            s, c = tls13.contexts(ca, crt, key, mutual=True, leaf_only=leaf)
            gc.disable(); t0 = time.perf_counter_ns()
            r = tls13.memory_handshake(s, c)
            t = (time.perf_counter_ns() - t0) / 1e3; gc.enable()
            if i >= cfg["warmup"]:
                times.append(t)
            if last is not None and r[:2] != last[:2]:
                raise SystemExit("handshake byte count not constant")
            last = r
        cb, sb, grp, cipher = last
        if tls13.GROUP_IDS.get(grp, "").lower() != group.lower():
            raise SystemExit(f"negotiated group {hex(grp)} != {group}")
        # chain lengths received by each side
        ci, co, si, so = (ssl.MemoryBIO() for _ in range(4))
        s, c = tls13.contexts(ca, crt, key, mutual=True, leaf_only=leaf)
        C = c.wrap_bio(ci, co, server_hostname="rtu-07"); S = s.wrap_bio(si, so, server_side=True)
        for _ in range(10):
            for o, src, dst in ((C, co, si), (S, so, ci)):
                try:
                    o.do_handshake()
                except ssl.SSLWantReadError:
                    pass
                dst.write(src.read())
        sm = summarize(times)
        rows.append({"group": group, "variant": v, "cipher": cipher, "bytes_c2s": cb, "bytes_s2c": sb, "bytes_total": cb + sb,
                     "chain_len_server_to_client": len(C.get_unverified_chain()), "chain_len_client_to_server": len(S.get_unverified_chain()),
                     "cpu_us_median": sm["median"], "cpu_us_p99": sm["p99"], "n": sm["n"]})
    json.dump(rows, open(out, "w"))


def main(path):
    cfg = load_config(path)
    run = start(cfg["exp_id"], cfg)
    from baselines import tls13
    rows = []
    for g in cfg["groups"]:
        conf = os.path.join(run, f"openssl_{g}.cnf"); open(conf, "w").write(tls13.OPENSSL_CONF_TEMPLATE.format(groups=g))
        out = os.path.join(run, f"rows_{g}.json")
        env = dict(os.environ, OPENSSL_CONF=conf)
        subprocess.run([sys.executable, __file__, "--child", path, g, out], env=env, check=True)
        rows += json.load(open(out))
    with open(os.path.join(run, "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r)
    finish(run)
    print(run)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child(load_config(sys.argv[2]), sys.argv[3], sys.argv[4])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "experiments", "configs", "EXP-013_tls_chain_matched.json"))
