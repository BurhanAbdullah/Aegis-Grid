"""Architecture/flow diagrams from one spec -> editable draw.io (.drawio) + 600 dpi PNG/PDF.
The PNG is drawn with matplotlib from the same coordinates, so both files show the same content."""
import os, html
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(__file__), "..", "figures", "diagrams")
FILL = {"snd": "#dbe8f8", "rcv": "#d7f0e6", "net": "#fde4d9", "pki": "#f3f2ee", "warn": "#fbe9c2", "plain": "#ffffff"}
EDGE = "#3a3a38"


def drawio(name, W, H, boxes, arrows):
    cells, nid = [], 2
    ids = {}
    for b in boxes:
        k, x, y, w, h, text, style = b
        ids[k] = f"n{nid}"; nid += 1
        dash = "dashed=1;" if style.endswith("_d") else ""
        fill = FILL[style.replace("_d", "")]
        cells.append(f'<mxCell id="{ids[k]}" value="{html.escape(text).replace(chr(10), "&lt;br&gt;")}" '
                     f'style="rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={EDGE};fontSize=11;{dash}" vertex="1" parent="1">'
                     f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    for a in arrows:
        s, t, label = a[:3]
        dashed = "dashed=1;" if len(a) > 3 and a[3] == "d" else ""
        cells.append(f'<mxCell id="e{nid}" value="{html.escape(label)}" style="endArrow=block;html=1;strokeColor={EDGE};fontSize=10;{dashed}" '
                     f'edge="1" parent="1" source="{ids[s]}" target="{ids[t]}"><mxGeometry relative="1" as="geometry"/></mxCell>')
        nid += 1
    xml = (f'<mxfile host="aegis-grid make_diagrams.py"><diagram name="{name}"><mxGraphModel dx="{W}" dy="{H}" grid="1" '
           f'gridSize="10" pageWidth="{W}" pageHeight="{H}"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
           + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>")
    open(os.path.join(OUT, name + ".drawio"), "w").write(xml)


def raster(name, W, H, boxes, arrows, width_in):
    fig = plt.figure(figsize=(width_in, width_in * H / W))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    geo = {}
    for k, x, y, w, h, text, style in boxes:
        geo[k] = (x, y, w, h)
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=6", fc=FILL[style.replace("_d", "")],
                                    ec=EDGE, lw=0.8, ls="--" if style.endswith("_d") else "-"))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=6.3, color="#0b0b0b", wrap=True)
    for a in arrows:
        s, t, label = a[:3]
        xs, ys, ws, hs = geo[s]; xt, yt, wt, ht = geo[t]
        cs, ct = (xs + ws / 2, ys + hs / 2), (xt + wt / 2, yt + ht / 2)

        def edge_pt(c, o, g):
            x, y, w, h = g; dx, dy = o[0] - c[0], o[1] - c[1]
            if dx == 0 and dy == 0:
                return c
            sx = (w / 2) / abs(dx) if dx else 1e9; sy = (h / 2) / abs(dy) if dy else 1e9; f = min(sx, sy)
            return (c[0] + dx * f, c[1] + dy * f)
        p0, p1 = edge_pt(cs, ct, geo[s]), edge_pt(ct, cs, geo[t])
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=7, color=EDGE, lw=0.8,
                                     ls="--" if len(a) > 3 and a[3] == "d" else "-"))
        if label:
            ax.text((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 4, label, ha="center", va="bottom", fontsize=5.5, color="#52514e",
                    bbox=dict(fc="white", ec="none", pad=0.6))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), dpi=600)
    plt.close(fig)


def make(name, W, H, boxes, arrows, width_in=7.0):
    os.makedirs(OUT, exist_ok=True)
    drawio(name, W, H, boxes, arrows); raster(name, W, H, boxes, arrows, width_in)
    print(name)


# ---- Fig. 1: merged architecture with the L1 key-establishment interaction (R1: Figs 1-2 redundant, KEM missing)
B1 = [
    ("app", 20, 20, 200, 40, "Control application\n(EMS / AGC / SCADA master)\nmessage M, deadline D", "snd"),
    ("l2", 20, 80, 200, 46, "L2  package-transform AONT\nY = AONT(M); RS(k,n) -> n shards", "snd"),
    ("l1", 20, 146, 200, 46, "L1/L5  AGP/1 record layer\nAES-256-GCM; epoch, seq,\nt_gen and deadline authenticated", "snd"),
    ("l34", 20, 212, 200, 46, "L3/L4  fixed-size records,\nconstant interval Δ, encrypted\ndummies, EDF queue, late drop", "snd"),
    ("l6s", 20, 278, 200, 36, "L6  CAP + bounded policy: sets n\nof L2 (k never lowered)", "snd"),
    ("net", 270, 212, 160, 46, "Untrusted IP network\n(passive observer, active\nattacker: drop/delay/replay/inject)", "net"),
    ("hs", 270, 100, 160, 64, "L1  AGP/1 handshake\nML-KEM-768/1024 (± X25519)\nML-DSA-44/65/87 transcript sig.\nX.509, pinned grid CA", "pki"),
    ("r1", 480, 212, 200, 46, "L1/L5  open record: AEAD, session,\nreplay window, epoch,\ndeadline + clock skew", "rcv"),
    ("r2", 480, 146, 200, 46, "L2  RS decode from any k shards;\nAONT inverse with canary;\nexactly-once delivery", "rcv"),
    ("r7", 480, 80, 200, 46, "L7  U = M̂ if valid before D,\nelse U_safe (hold last validated\nset-point; droop active)", "rcv"),
    ("plant", 480, 20, 200, 40, "Plant / actuator\n(governor set-point, relay, RTU)", "rcv"),
    ("l6r", 480, 278, 200, 36, "L6  observables: gaps, deadline\nmisses, rejected records", "rcv"),
]
A1 = [("app", "l2", ""), ("l2", "l1", ""), ("l1", "l34", ""), ("l34", "net", "records"), ("net", "r1", ""),
      ("r1", "r2", "valid records"), ("r2", "r7", "M̂ or ⊥"), ("r7", "plant", "U"), ("hs", "l1", "traffic secrets", "d"),
      ("hs", "r1", "traffic secrets", "d"), ("l6r", "l6s", "pressure feedback", "d")]

# ---- Fig. 2: AGP/1 handshake sequence
B2 = [
    ("I", 40, 10, 170, 34, "Initiator (control centre cc-01)", "snd"), ("R", 470, 10, 170, 34, "Responder (RTU rtu-07)", "rcv"),
    ("i1", 20, 60, 210, 46, "ephemeral ML-KEM keypair (ek, dk)\n[+ X25519 share]; offered suites", "snd"),
    ("r1", 450, 120, 210, 66, "select suite; (ct, ss) = Encaps(ek)\n[+ X25519]; sign transcript with\nML-DSA (cert R); Finished_R", "rcv"),
    ("i2", 20, 200, 210, 66, "verify cert R (pinned CA), signature,\nFinished_R, downgrade rule;\nss = Decaps(dk, ct); sign; Finished_I", "snd"),
    ("r2", 450, 290, 210, 46, "verify cert I, signature,\nFinished_I -> traffic secrets", "rcv"),
    ("k", 200, 350, 280, 40, "HKDF key schedule -> i2r / r2i traffic keys,\nsession id; ephemeral keys erased", "pki"),
]
A2 = [("i1", "r1", "ClientHello: suites, ek, nonce, ids"), ("r1", "i2", "ServerHello: suite, ct, supported, cert, sig, Finished"),
      ("i2", "r2", "ClientFinish: cert, sig, Finished"), ("i2", "k", "", "d"), ("r2", "k", "", "d")]

# ---- Fig. 5: receiver decision flow (L5-L7) - fail-secure semantics
B5 = [
    ("in", 230, 10, 200, 30, "record arrives", "plain"),
    ("auth", 230, 60, 200, 34, "AEAD tag, session id, version valid?", "plain"),
    ("rep", 230, 114, 200, 34, "sequence inside replay window,\nnot seen before?", "plain"),
    ("dl", 230, 168, 200, 34, "now ≤ t_gen + D + skew?", "plain"),
    ("k", 230, 222, 200, 34, "≥ k consistent shards for msg_id?", "plain"),
    ("aont", 230, 276, 200, 34, "RS decode + AONT canary/length ok?", "plain"),
    ("ok", 230, 330, 200, 34, "deliver M̂ once; U = M̂", "rcv"),
    ("rej", 500, 168, 170, 46, "reject record, count reason\n(no state change)", "warn"),
    ("wait", 20, 222, 170, 46, "wait for more shards;\nat D: M̂ = ⊥", "plain"),
    ("safe", 20, 330, 170, 34, "U = U_safe (hold last valid)", "warn"),
]
A5 = [("in", "auth", ""), ("auth", "rep", "yes"), ("rep", "dl", "yes"), ("dl", "k", "yes"), ("k", "aont", "yes"),
      ("aont", "ok", "yes"), ("auth", "rej", "no"), ("rep", "rej", "no"), ("dl", "rej", "no"), ("aont", "rej", "no"),
      ("k", "wait", "no"), ("wait", "safe", "deadline")]

# ---- Fig. 7a: CAP adaptation policy state machine
B7 = [
    ("obs", 20, 20, 220, 46, "observables o_k per epoch\n(loss, deadline misses, rejects)", "plain"),
    ("z", 20, 90, 220, 46, "z = (o − μ)/σ  (benign calibration)\ne_k = mean(max(0, z))", "plain"),
    ("cap", 20, 160, 220, 46, "CAP_k = α·CAP_{k−1} + e_k\n(= EWMA_k / (1−α))", "plain"),
    ("N", 320, 60, 180, 46, "NORMAL\n(k, n_normal) = (5, 7)", "snd"),
    ("P", 320, 160, 180, 46, "PROTECT\n(k, n_protect) = (5, 10)", "warn"),
]
A7 = [("obs", "z", ""), ("z", "cap", ""), ("cap", "P", "CAP ≥ θ"), ("N", "P", "alarm"), ("P", "N", "H alarm-free epochs")]

if __name__ == "__main__":
    make("Fig1_architecture", 700, 330, B1, A1)
    make("Fig2_handshake_sequence", 680, 400, B2, A2)
    make("Fig4_receiver_fail_secure_flow", 690, 380, B5, A5, 5.5)
    make("Fig3_cap_policy", 520, 220, B7, A7, 5.0)
