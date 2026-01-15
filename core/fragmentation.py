import random
from core.packet import Packet

def fragment_message(data: bytes, n_fragments: int, dummy_ratio: float):
    fragments = []
    size = len(data) // n_fragments

    for i in range(n_fragments):
        fragment = data[i*size:(i+1)*size]
        fragments.append(Packet.create(fragment, False))

    dummy_count = int(n_fragments * dummy_ratio * 2)
    for _ in range(dummy_count):
        fragments.append(Packet.create(b"\x00" * size, True))

    random.shuffle(fragments)
    return fragments
