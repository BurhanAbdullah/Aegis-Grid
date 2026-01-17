from core.signature import SignatureEngine
from core.packet import Packet
import os
import random

def generate_traffic(agent, data, dummy_ratio):
    assert hasattr(agent, "fragment_count"), "Agent contract violated"

    signer = SignatureEngine()
    msg_id = os.urandom(8)
    fragments = []

    for i, b in enumerate(data):
        layer_key = agent.get_layer_key(i)

        pkt = Packet(
            msg_id=msg_id,
            frag_id=i,
            total_frags=agent.fragment_count,
            payload=bytes([b])
        )

        pkt.signature = signer.sign(pkt.signable(), layer_key)
        fragments.append(pkt)

    # dummy traffic
    dummy_count = int(len(fragments) * dummy_ratio)
    for _ in range(dummy_count):
        i = random.randint(0, len(data)-1)
        pkt = Packet(msg_id, i, agent.fragment_count, os.urandom(1))
        pkt.signature = signer.sign(pkt.signable(), agent.get_layer_key(i))
        fragments.append(pkt)

    return fragments
