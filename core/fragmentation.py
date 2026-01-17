import os
import random
from core.packet import Packet
from core.signature import SignatureEngine

def fragment_message(data, n_fragments, dummy_ratio, key):
    signer = SignatureEngine()
    msg_id = os.urandom(8)
    fragments = []

    size = max(1, len(data) // n_fragments)

    # Real fragments
    for i in range(n_fragments):
        frag = data[i*size:(i+1)*size]
        pkt = Packet.create(msg_id, i, n_fragments, frag, False)
        pkt.signature = signer.sign(pkt.signable(), key)
        fragments.append(pkt)

    # Dummy fragments (use valid ID space but flagged)
    dummy_count = int(n_fragments * dummy_ratio)
    for i in range(dummy_count):
        dummy_payload = os.urandom(size)
        pkt = Packet.create(msg_id, n_fragments + i, n_fragments, dummy_payload, True)
        pkt.signature = signer.sign(pkt.signable(), key)
        fragments.append(pkt)

    random.shuffle(fragments)
    return fragments
