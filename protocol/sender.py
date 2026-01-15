import os
from core.fragmentation import fragment_message
from core.crypto import CryptoEngine
from core.key_schedule import derive_layer_keys

def generate_traffic(agent, message: bytes, dummy_ratio: float):
    crypto = CryptoEngine()
    nonce = os.urandom(16)
    agent.last_nonce = nonce

    # 🔒 IDLE TRAFFIC CASE
    if message is None:
        fake_payload = b"\x00" * 256
        packets = fragment_message(
            fake_payload,
            agent.fragment_count,
            dummy_ratio,
            agent.master_key
        )
        agent.expected_real_fragments = 0
        return packets

    # 🔐 REAL MESSAGE CASE
    keys = derive_layer_keys(agent.master_key, nonce)
    data = message

    for k in keys:
        data = crypto.encrypt(data, k)

    packets = fragment_message(
        data,
        agent.fragment_count,
        dummy_ratio,
        agent.master_key
    )

    agent.expected_real_fragments = sum(not p.is_dummy for p in packets)
    return packets
