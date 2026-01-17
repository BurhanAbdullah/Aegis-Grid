import random
import os
from core.packet import Packet

def inject_adversary(packets, forge_ratio=0.0, replay_ratio=0.0):
    out = []

    for p in packets:
        r = random.random()

        # ---- FORGERY: invalid signature ----
        if r < forge_ratio:
            forged = Packet(
                msg_id=p.msg_id,
                frag_id=p.frag_id,
                total_frags=p.total_frags,
                payload=os.urandom(len(p.payload)),
                is_dummy=False,
                signature=os.urandom(64)  # INVALID signature
            )
            out.append(forged)

        # ---- REPLAY ----
        elif r < forge_ratio + replay_ratio:
            out.append(p)
            out.append(p)  # duplicate

        # ---- HONEST ----
        else:
            out.append(p)

    random.shuffle(out)
    return out
