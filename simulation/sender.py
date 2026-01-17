import random
from core.packet import Packet

def send_message(message: bytes, loss_rate: float = 0.0):
    packets = []
    total = len(message)

    for i, b in enumerate(message):
        if random.random() < loss_rate:
            continue

        packets.append(
            Packet(
                msg_id=1,
                frag_id=i,
                total_frags=total,
                payload=bytes([b]),
                is_dummy=False,
                signature=b"valid"
            )
        )

    return packets
