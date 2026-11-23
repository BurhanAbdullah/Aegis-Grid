"""EXP-002 — CPU timing of cryptographic operations and of the complete AGP/1
handshake and record path, on the machine described in environment.json.

Label for every number produced: HARDWARE MEASUREMENT on a virtualised x86-64
cloud VM. These are *not* embedded (RTU/IED/Cortex-M) measurements.

Run: python3 experiments/runners/exp002_crypto_bench.py [config]
"""
import csv, gc, json, os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from experiments.common import start, finish, summarize, load_config, ROOT

from cryptography.hazmat.primitives.asymmetric import mlkem, mldsa, x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509

from aegis_pq.clock import SystemClock
from aegis_pq.pki import GridCA, validate_peer_cert
from aegis_pq.handshake import Initiator, Responder
from aegis_pq.channel import SecureChannel, ChannelConfig
from aegis_pq.suites import SUITES, Policy

pc = time.perf_counter_ns


def timeit(fn, n, warmup):
    for _ in range(warmup):
        fn()
    out = []
    gc.disable()
    try:
        for _ in range(n):
            t0 = pc(); fn(); out.append((pc() - t0) / 1e3)   # microseconds
    finally:
        gc.enable()
    return out


def main(cfg_path):
    cfg = load_config(cfg_path)
    run = start(cfg["exp_id"], cfg)
    W, NF, NS, NH = cfg["warmup"], cfg["n_fast"], cfg["n_slow"], cfg["n_handshake"]
    raw = {}

    # ---- ML-KEM
    for name, cls, pcls in (("ML-KEM-768", mlkem.MLKEM768PrivateKey, mlkem.MLKEM768PublicKey),
                            ("ML-KEM-1024", mlkem.MLKEM1024PrivateKey, mlkem.MLKEM1024PublicKey)):
        sk = cls.generate(); pk = sk.public_key(); ss, ct = pk.encapsulate(); pkb = pk.public_bytes_raw()
        raw[f"{name} keygen"] = timeit(cls.generate, NS, W)
        raw[f"{name} encaps"] = timeit(pk.encapsulate, NF, W)
        raw[f"{name} decaps"] = timeit(lambda: sk.decapsulate(ct), NF, W)
        raw[f"{name} pk deserialize"] = timeit(lambda: pcls.from_public_bytes(pkb), NF, W)
    # ---- ML-DSA
    msg = os.urandom(48)
    for name, cls in (("ML-DSA-44", mldsa.MLDSA44PrivateKey), ("ML-DSA-65", mldsa.MLDSA65PrivateKey),
                      ("ML-DSA-87", mldsa.MLDSA87PrivateKey)):
        sk = cls.generate(); pk = sk.public_key(); sig = sk.sign(msg)
        raw[f"{name} keygen"] = timeit(cls.generate, NS, W)
        raw[f"{name} sign"] = timeit(lambda: sk.sign(msg), NS, W)
        raw[f"{name} verify"] = timeit(lambda: pk.verify(sig, msg), NF, W)
    # ---- X25519 (hybrid component)
    a = x25519.X25519PrivateKey.generate(); bpub = x25519.X25519PrivateKey.generate().public_key()
    raw["X25519 keygen"] = timeit(x25519.X25519PrivateKey.generate, NF, W)
    raw["X25519 exchange"] = timeit(lambda: a.exchange(bpub), NF, W)
    # ---- KDF
    prk = os.urandom(48)
    raw["HKDF-SHA384 expand 48B"] = timeit(lambda: HKDFExpand(hashes.SHA384(), 48, b"AGP1 x").derive(prk), NF, W)
    # ---- AEAD
    key = AESGCM(os.urandom(32)); nonce = os.urandom(12); aad = os.urandom(20)
    for n in cfg["aead_payload_bytes"]:
        pt = os.urandom(n); ctx = key.encrypt(nonce, pt, aad)
        raw[f"AES-256-GCM encrypt {n}B"] = timeit(lambda: key.encrypt(nonce, pt, aad), NF, W)
        raw[f"AES-256-GCM decrypt {n}B"] = timeit(lambda: key.decrypt(nonce, ctx, aad), NF, W)
    # ---- certificates
    clock = SystemClock()
    ca = GridCA()
    cred = ca.issue("rtu-07", "ML-DSA-65")
    raw["X.509 DER parse (ML-DSA-65 cert)"] = timeit(lambda: x509.load_der_x509_certificate(cred.cert_der), NF, W)
    raw["X.509 validate (ML-DSA-65 cert)"] = timeit(
        lambda: validate_peer_cert(cred.cert_der, ca.cert, "rtu-07", "ML-DSA-65", clock.now_ms()), NS, W)

    # ---- complete handshake per suite (in-memory, both parties' CPU, no network)
    creds_i = [ca.issue("cc-01", a) for a in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")]
    creds_r = [ca.issue("rtu-07", a) for a in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")]
    sizes = {}
    hs_parts = {}
    for code in cfg["suites"]:
        s = SUITES[code]
        pol = Policy(preference=(code,), min_category=s.nist_category)
        parts = {"initiator: build ClientHello": [], "responder: process ClientHello": [],
                 "initiator: process ServerHello": [], "responder: process ClientFinish": [], "total CPU": []}
        for k in range(W + NH):
            t0 = pc(); i = Initiator("cc-01", "rtu-07", creds_i, ca.cert, clock, policy=pol); ch = i.client_hello(); t1 = pc()
            r = Responder("rtu-07", creds_r, ca.cert, clock, policy=pol); sh = r.process_client_hello(ch); t2 = pc()
            cf = i.process_server_hello(sh); t3 = pc()
            r.process_client_finish(cf); t4 = pc()
            if k >= W:
                for key_, v in zip(parts, ((t1 - t0), (t2 - t1), (t3 - t2), (t4 - t3), (t4 - t0))):
                    parts[key_].append(v / 1e3)
        sizes[s.name] = i.keys.sizes
        for p, v in parts.items():
            raw[f"handshake {s.name}: {p}"] = v
        # ---- record path with the negotiated keys
        a_ch, b_ch = SecureChannel(i.keys, clock), SecureChannel(r.keys, clock)
        for n in cfg["aead_payload_bytes"]:
            payload = os.urandom(n)
            recs = []
            raw[f"record seal {n}B ({s.name})"] = timeit(lambda: recs.append(a_ch.seal(payload, 1e6)), NF, W)
            it = iter(recs)
            raw[f"record open {n}B ({s.name})"] = timeit(lambda: b_ch.open(next(it)), NF, W) if len(recs) >= NF + W else []

    # ---- write raw samples (long format) and summary
    with open(os.path.join(run, "samples_us.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["operation", "sample_index", "time_us"])
        for op, v in raw.items():
            for j, x in enumerate(v):
                w.writerow([op, j, f"{x:.3f}"])
    summ = {op: summarize(v) for op, v in raw.items() if v}
    with open(os.path.join(run, "summary_us.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["operation", "n", "mean_us", "median_us", "std_us", "p95_us", "p99_us", "min_us", "max_us"])
        for op, s_ in summ.items():
            w.writerow([op, s_["n"], *(f"{s_[k]:.3f}" for k in ("mean", "median", "std", "p95", "p99", "min", "max"))])
    sz = {}
    for name, d in sizes.items():
        sz[name] = dict(d, total=sum(d.values()))
    json.dump(sz, open(os.path.join(run, "handshake_wire_bytes.json"), "w"), indent=2)
    finish(run)
    print(run)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "experiments", "configs", "EXP-002_crypto_bench.json"))
