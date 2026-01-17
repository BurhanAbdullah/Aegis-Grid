import random
from core.packet import Packet

def fragment_message(data, n_fragments, dummy_ratio, key):
    fragments = []
    size = max(1, len(data) // n_fragments)

    for i in range(n_fragments):
        frag = data[i*size:(i+1)*size]
        fragments.append(Packet.create(frag, False, b"SIG"))

    for _ in range(int(n_fragments * dummy_ratio)):
        fragments.append(Packet.create(b"DUMMY", True, b"SIG"))

    random.shuffle(fragments)
    return fragments
