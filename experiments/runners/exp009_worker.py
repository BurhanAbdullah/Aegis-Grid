"""EXP-009 worker: one protocol configuration, measured over real loopback sockets
between two processes (fork). Invoked by exp009_protocol_baselines.py with
OPENSSL_CONF already set for TLS group selection. Prints one JSON object.

Timing: CLOCK_MONOTONIC (time.monotonic_ns) is shared by both processes, so
one-way latency = receiver app-level receive time − sender app-level send time.
"""
import json, multiprocessing as mp, os, socket, struct, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np

mono = time.monotonic_ns
LEN = struct.Struct(">I")


def recv_exact(s, n):
    b = b""
    while len(b) < n:
        c = s.recv(n - len(b))
        if not c:
            raise EOFError
        b += c
    return b


def frame_send(s, b):
    s.sendall(LEN.pack(len(b)) + b)


def frame_recv(s):
    return recv_exact(s, LEN.unpack(recv_exact(s, 4))[0])


def summarize(x):
    x = np.asarray(x, float)
    return {"n": int(x.size), "median": float(np.median(x)), "mean": float(x.mean()), "p95": float(np.percentile(x, 95)),
            "p99": float(np.percentile(x, 99)), "max": float(x.max()), "min": float(x.min())}


def wait_until(t):
    while True:
        d = t - mono()
        if d <= 0:
            return
        if d > 400_000:
            time.sleep((d - 300_000) / 1e9)


# ------------------------------------------------------------------ TLS 1.3
def tls_run(a):
    import ssl
    from baselines import tls13
    ca, crt, key = tls13.make_pki(a["tmp"], a["sig"])
    sctx, cctx = tls13.contexts(ca, crt, key)
    cb, sb, grp, cipher = tls13.memory_handshake(sctx, cctx)
    ls = socket.socket(); ls.bind(("127.0.0.1", 0)); ls.listen(64); port = ls.getsockname()[1]
    q = mp.Queue()

    def server():
        lat = []
        for i in range(a["handshakes"] + 1):
            c, _ = ls.accept(); c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            t = sctx.wrap_socket(c, server_side=True)
            if i == a["handshakes"]:
                for _ in range(a["messages"]):
                    d = recv_exact(t, 8 + a["msg_bytes"]); lat.append((mono() - struct.unpack(">Q", d[:8])[0]) / 1e3)
            t.close()
        q.put(lat)
    p = mp.Process(target=server); p.start()
    hs = []
    for i in range(a["handshakes"] + 1):
        t0 = mono()
        c = socket.create_connection(("127.0.0.1", port)); c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        t = cctx.wrap_socket(c, server_hostname="rtu-07")
        if i < a["handshakes"]:
            hs.append((mono() - t0) / 1e3); t.close(); continue
        nxt = mono()
        for _ in range(a["messages"]):
            nxt += int(a["gap_ms"] * 1e6); wait_until(nxt)
            t.sendall(struct.pack(">Q", mono()) + os.urandom(a["msg_bytes"]))
        time.sleep(0.2); t.close()
    lat = q.get(); p.join()
    per_record = 5 + 1 + 16           # TLS 1.3 record header + inner content type + AEAD tag
    return {"protocol": "TLS 1.3", "group": tls13.GROUP_IDS.get(grp, hex(grp)), "cert": a["sig"], "cipher": cipher,
            "handshake_bytes_c2s": cb, "handshake_bytes_s2c": sb, "handshake_wall_us": summarize(hs),
            "oneway_us": summarize(lat), "wire_bytes_per_message": a["msg_bytes"] + 8 + per_record + 40,
            "transport": "TCP (TCP_NODELAY)", "note": "wire bytes include 40 B IPv4+TCP header, no options"}


# ------------------------------------------------------------------ AGP/1
def agp_run(a):
    from aegis_pq.channel import ChannelConfig, SecureChannel
    from aegis_pq.clock import SystemClock
    from aegis_pq.handshake import Initiator, Responder
    from aegis_pq.pipeline import Sender, Receiver, body_size_for
    from aegis_pq.pki import GridCA
    from aegis_pq.suites import Policy
    clock = SystemClock()
    ca = GridCA(sig_alg=a["sig_alg"]); ci = ca.issue("cc-01", a["sig_alg"]); cr = ca.issue("rtu-07", a["sig_alg"])
    pol = Policy((a["suite"],), min_category=1)
    ls = socket.socket(); ls.bind(("127.0.0.1", 0)); ls.listen(64); port = ls.getsockname()[1]
    us = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); us.bind(("127.0.0.1", 0)); uport = us.getsockname()[1]
    q = mp.Queue()
    k, n = a["k"], a["n"]

    def server():
        keys = None
        for i in range(a["handshakes"] + 1):
            c, _ = ls.accept(); c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            r = Responder("rtu-07", [cr], ca.cert, clock, pol)
            frame_send(c, r.process_client_hello(frame_recv(c)))
            keys = r.process_client_finish(frame_recv(c)); frame_send(c, b"ok"); c.close()
        rx = Receiver(SecureChannel(keys, clock, ChannelConfig(body_size=body_size_for(a["msg_bytes"] + 8, k))))
        lat, got = [], 0
        us.settimeout(2.0)
        try:
            while got < a["messages"]:
                d = us.recv(4096)
                r = rx.receive(d)
                if r is not None:
                    lat.append((mono() - struct.unpack(">Q", r[1][:8])[0]) / 1e3); got += 1
        except socket.timeout:
            pass
        q.put(lat)
    p = mp.Process(target=server); p.start()
    hs, sizes = [], None
    for i in range(a["handshakes"] + 1):
        t0 = mono()
        c = socket.create_connection(("127.0.0.1", port)); c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        ini = Initiator("cc-01", "rtu-07", [ci], ca.cert, clock, pol)
        ch = ini.client_hello(); frame_send(c, ch)
        sh = frame_recv(c); cf = ini.process_server_hello(sh); frame_send(c, cf); frame_recv(c)
        dt = (mono() - t0) / 1e3; c.close()
        sizes = (len(ch) + len(cf), len(sh))
        if i < a["handshakes"]:
            hs.append(dt)
    time.sleep(0.1)
    tx = Sender(SecureChannel(ini.keys, clock, ChannelConfig(body_size=body_size_for(a["msg_bytes"] + 8, k))), k, n)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); dst = ("127.0.0.1", uport)
    nxt, rec_len = mono(), None
    for _ in range(a["messages"]):
        nxt += int(a["gap_ms"] * 1e6); wait_until(nxt)
        m = struct.pack(">Q", mono()) + os.urandom(a["msg_bytes"])
        _, recs = tx.seal_message(m, a["deadline_ms"])
        for r in recs:
            s.sendto(r, dst)
        rec_len = len(recs[0])
    lat = q.get(); p.join()
    return {"protocol": "AGP/1", "suite": hex(a["suite"]), "sig_alg": a["sig_alg"], "k": k, "n": n,
            "handshake_bytes_c2s": sizes[0], "handshake_bytes_s2c": sizes[1], "handshake_wall_us": summarize(hs),
            "oneway_us": summarize(lat), "messages_delivered": len(lat), "messages_sent": a["messages"],
            "wire_bytes_per_message": n * (rec_len + 28), "transport": "handshake TCP, records UDP",
            "note": "one-way latency = first k fragments received, decrypted, RS-decoded and AONT-inverted; wire bytes include 28 B IPv4+UDP header"}


# ------------------------------------------------------------------ HMAC baseline
def hmac_run(a):
    from baselines.iec62351_hmac import HmacSender, HmacReceiver
    key = os.urandom(32)
    us = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); us.bind(("127.0.0.1", 0)); port = us.getsockname()[1]
    q = mp.Queue()

    def server():
        rx, lat = HmacReceiver(key, 10 ** 9), []
        us.settimeout(2.0)
        try:
            while len(lat) < a["messages"]:
                d = us.recv(4096); m = rx.open(d, mono() // 1000)
                if m is not None:
                    lat.append((mono() - struct.unpack(">Q", m[:8])[0]) / 1e3)
        except socket.timeout:
            pass
        q.put(lat)
    p = mp.Process(target=server); p.start(); time.sleep(0.1)
    tx = HmacSender(key); s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); dst = ("127.0.0.1", port)
    nxt = mono()
    for _ in range(a["messages"]):
        nxt += int(a["gap_ms"] * 1e6); wait_until(nxt)
        r = tx.seal(struct.pack(">Q", mono()) + os.urandom(a["msg_bytes"]), mono() // 1000); s.sendto(r, dst)
    lat = q.get(); p.join()
    return {"protocol": "IEC 62351-6-style HMAC (simplified)", "oneway_us": summarize(lat), "messages_delivered": len(lat),
            "wire_bytes_per_message": len(r) + 28, "transport": "UDP", "confidentiality": False, "key_establishment": "pre-shared group key (out of scope)"}


if __name__ == "__main__":
    mp.set_start_method("fork")
    a = json.loads(sys.argv[1])
    print(json.dumps({"tls": tls_run, "agp": agp_run, "hmac": hmac_run}[a["mode"]](a)))
