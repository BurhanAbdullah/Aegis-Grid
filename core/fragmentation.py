import random
from core.packet import Packet
from core.crypto import CryptoEngine

def fragment_message(data: bytes, n_fragments: int, dummy_ratio: float, mac_key: bytes):
    crypto = CryptoEngine()
    fragments = []

    size = len(data) // n_fragments
    for i in range(n_fragments):
        fragment = data[i*size:(i+1)*size]
        mac = crypto.mac(fragment, mac_key)
        fragments.append(Packet.create(fragment, False, mac))

    dummy_count = int(n_fragments * dummy_ratio)
    for _ in range(dummy_count):
        dummy_payload = b"\x00" * size
        dummy_mac = crypto.mac(dummy_payload, mac_key)
        fragments.append(Packet.create(dummy_payload, True, dummy_mac))

    random.shuffle(fragments)
    return fragments
