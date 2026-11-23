"""EXP-005 — capture real UDP-loopback traces (HARDWARE MEASUREMENT on the VM).

For each session and condition a fresh AGP/1 handshake (suite 0x0101) is run,
then a sender process emits the scheduled workload over UDP to a receiver
process on 127.0.0.1. The receiver timestamps every datagram with
CLOCK_MONOTONIC (the passive observer's view: arrival time and size). After the
session the main process decrypts and reassembles the captured datagrams with
the real Receiver to measure delivery, end-to-end latency and deadline drops.

Conditions
  unshaped    variable-size records, sent when generated
  padded      fixed-size records, sent when generated
  shaped_2ms  fixed-size records, one record every 2 ms (dummies when idle, EDF)
  shaped_1ms  as above, 1 ms
Condition order is randomised per session to avoid drift confounds.
"""
import csv, gzip, json, multiprocessing as mp, os, socket, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np
from experiments.common import start, finish, load_config, ROOT
from aegis_pq.channel import ChannelConfig, SecureChannel
from aegis_pq.clock import ManualClock
from aegis_pq.handshake import Initiator, Responder, run_handshake
from aegis_pq.pipeline import Sender, Receiver, body_size_for
from aegis_pq.pki import GridCA
from aegis_pq.shaping import ConstantRateShaper

END = b"\xffEND"
OFFSET_MS = (time.time_ns() - time.monotonic_ns()) / 1e6


class MonoClock:
    """Monotonic clock expressed as wall-like ms (same timebase in all processes)."""
    def now_ms(self):
        return time.monotonic_ns() / 1e6 + OFFSET_MS

    def mono_ns(self):
        return time.monotonic_ns()


def wait_until(t_ns):
    while True:
        d = t_ns - time.monotonic_ns()
        if d <= 0:
            return
        if d > 400_000:
            time.sleep((d - 300_000) / 1e9)


def receiver_proc(port_q, out_conn):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8 << 20)
    s.bind(("127.0.0.1", 0))
    port_q.put(s.getsockname()[1])
    got = []
    while True:
        d = s.recv(4096)
        t = time.monotonic_ns()
        if d == END:
            break
        got.append((t, d))
    out_conn.send(got)
    out_conn.close()


def schedule(cfg, rng):
    w = cfg["workload_ASSUMPTION"]
    nwin = int(cfg["session_s"] * 1000 / cfg["window_ms"])
    labels = rng.integers(0, 3, nwin)
    msgs = []                                   # (t_ms, class, bytes, deadline_ms)
    t = rng.uniform(0, w["telemetry"]["period_ms"])
    while t < cfg["session_s"] * 1000:
        msgs.append((t, "telemetry", w["telemetry"]["bytes"], w["telemetry"]["deadline_ms"])); t += w["telemetry"]["period_ms"]
    for i, lab in enumerate(labels):
        if lab == 0:
            continue
        c = "event" if lab == 1 else "command"
        t0 = i * cfg["window_ms"] + rng.uniform(*w["event_start_ms"])
        for o in w[c]["offsets_ms"]:
            msgs.append((t0 + o, c, w[c]["bytes"], w[c]["deadline_ms"]))
    msgs.sort()
    return labels, [(t, c, b, dl, rng.bytes(b)) for (t, c, b, dl) in msgs]


def run_condition(cfg, cond, msgs, pki):
    ca, ci, cr = pki
    clock = MonoClock()
    ki, kr = run_handshake(Initiator("cc-01", "rtu-07", [ci], ca.cert, clock),
                           Responder("rtu-07", [cr], ca.cert, clock))
    body = 0 if cond == "unshaped" else body_size_for(cfg["max_message_bytes"], cfg["k"])
    ccfg = ChannelConfig(body_size=body)
    tx = SecureChannel(ki, clock, ccfg)
    snd = Sender(tx, cfg["k"], cfg["n"])
    port_q, (rc, wc) = mp.Queue(), mp.Pipe(duplex=False)
    p = mp.Process(target=receiver_proc, args=(port_q, wc)); p.start()
    port = port_q.get()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dst = ("127.0.0.1", port)
    time.sleep(0.05)
    t0_ns = time.monotonic_ns() + 20_000_000
    t0_ms = t0_ns / 1e6 + OFFSET_MS
    meta, sends = {}, []                         # mid -> (class, gen_ms_rel, deadline)
    if cond in ("unshaped", "padded"):
        for (t, c, b, dl, m) in msgs:
            wait_until(t0_ns + int(t * 1e6))
            mid, recs = snd.seal_message(m, dl, t0_ms + t)
            meta[mid] = (c, t, dl)
            for r in recs:
                s.sendto(r, dst)
            sends.append((time.monotonic_ns() - t0_ns, mid))
    else:
        period = 2.0 if cond == "shaped_2ms" else 1.0
        sh = ConstantRateShaper(tx, period)
        end_ms = cfg["session_s"] * 1000 + cfg["drain_ms"]
        j, i = 0, 0
        while True:
            tt = i * period
            if tt > end_ms:
                break
            wait_until(t0_ns + int(tt * 1e6))
            while j < len(msgs) and msgs[j][0] <= tt:
                t, c, b, dl, m = msgs[j]
                mid, frags = snd.fragment(m)
                meta[mid] = (c, t, dl)
                for f in frags:
                    sh.enqueue(f, t0_ms + t, dl, tag=mid)
                j += 1
            rec, tag = sh.tick(clock.now_ms())
            s.sendto(rec, dst)
            i += 1
        sends.append(("shaper_stats", sh.stats))
    time.sleep(0.05)
    s.sendto(END, dst)
    got = rc.recv(); p.join()
    # offline decryption/reassembly with the receive timestamps
    mclock = ManualClock()
    rx = Receiver(SecureChannel(kr, mclock, ccfg))
    done = {}
    for (t, d) in got:
        mclock.t_ms = t / 1e6 + OFFSET_MS
        r = rx.receive(d)
        if r is not None:
            done[r[0]] = (t - t0_ns) / 1e6
    trace = [((t - t0_ns) / 1e6, len(d)) for (t, d) in got]
    rows = []
    for mid, (c, t, dl) in meta.items():
        lat = done[mid] - t if mid in done else None
        rows.append({"msg_id": mid, "class": c, "gen_ms": round(t, 4), "deadline_ms": dl,
                     "delivered": mid in done, "latency_ms": None if lat is None else round(lat, 4)})
    shaper = next((x[1] for x in sends if x[0] == "shaper_stats"), None)
    return trace, rows, {k.name if hasattr(k, "name") else str(k): v for k, v in rx.rejects.items()}, shaper, body


def main(path):
    cfg = load_config(path)
    run = start(cfg["exp_id"], cfg)
    rng = np.random.default_rng(cfg["seed"])
    from aegis_pq.clock import SystemClock
    now = MonoClock().now_ms()
    ca = GridCA(now_ms=now)
    pki = (ca, ca.issue("cc-01", now_ms=now), ca.issue("rtu-07", now_ms=now))
    tf = gzip.open(os.path.join(run, "traces.csv.gz"), "wt", newline="")
    mf = gzip.open(os.path.join(run, "messages.csv.gz"), "wt", newline="")
    tw = csv.writer(tf); tw.writerow(["session", "condition", "t_ms", "bytes"])
    mw = None
    lab_rows, summary = [], []
    for sess in range(cfg["sessions"]):
        labels, msgs = schedule(cfg, rng)
        lab_rows += [(sess, w, int(l)) for w, l in enumerate(labels)]
        order = list(rng.permutation(cfg["conditions"]))
        for cond in order:
            trace, rows, rej, shaper, body = run_condition(cfg, cond, msgs, pki)
            for t, b in trace:
                tw.writerow([sess, cond, round(t, 4), b])
            for r in rows:
                r.update(session=sess, condition=cond)
                if mw is None:
                    mw = csv.DictWriter(mf, fieldnames=list(r)); mw.writeheader()
                mw.writerow(r)
            summary.append({"session": sess, "condition": cond, "datagrams": len(trace),
                            "bytes": int(sum(b for _, b in trace)), "body_size": body,
                            "rejects": rej, "shaper": shaper,
                            "delivered": sum(r["delivered"] for r in rows), "messages": len(rows)})
            print(sess, cond, len(trace), summary[-1]["delivered"], "/", len(rows), rej, flush=True)
    tf.close(); mf.close()
    with open(os.path.join(run, "window_labels.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["session", "window", "label"]); w.writerows(lab_rows)
    with open(os.path.join(run, "session_summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    finish(run)
    print(run)


if __name__ == "__main__":
    mp.set_start_method("fork")
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "experiments", "configs", "EXP-005_traffic_capture.json"))
