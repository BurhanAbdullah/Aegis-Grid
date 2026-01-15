from core.crypto import CryptoEngine
from core.fragmentation import fragment_message
from core.key_schedule import derive_layer_keys
import os

def generate_traffic(agent, message: bytes, dummy_ratio: float):
    crypto = CryptoEngine()
    nonce = os.urandom(16)
    agent.last_nonce = nonce

    # -------------------------------
    # IDLE TRAFFIC (NO MESSAGE)
    # -------------------------------
    if message is None:
        packets = fragment_message(
            b"\x00" * 32,
            n_fragments=agent.fragment_count,
            dummy_ratio=1.0,
            signer=None
        )
        return packets

    # -------------------------------
    # ACTIVE TRAFFIC
    # -------------------------------
    keys = derive_layer_keys(agent.master_key, nonce)

    data = message
    for k in keys:
        data = crypto.encrypt(data, k)

    def signer(payload):
        return crypto.sign(payload, agent.master_key)

    packets = fragment_message(
        data,
        n_fragments=agent.fragment_count,
        dummy_ratio=dummy_ratio,
        signer=signer
    )

    agent.expected_real_fragments = sum(not p.is_dummy for p in packets)
    return packets
