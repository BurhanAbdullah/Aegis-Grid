from core.packet import Packet
import random

def fragment_message(data: bytes, n_fragments: int, dummy_ratio: float, signer=None):
    fragments = []
    size = len(data) // n_fragments

    for i in range(n_fragments):
        frag = data[i*size:(i+1)*size]
        sig = signer(frag) if signer else b""
        fragments.append(Packet.create(frag, False, sig))

    dummy_count = int(n_fragments * dummy_ratio)
    for _ in range(dummy_count):
        dummy = b"\x00" * size
        sig = signer(dummy) if signer else b""
        fragments.append(Packet.create(dummy, True, sig))

    random.shuffle(fragments)
    return fragments
