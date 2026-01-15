import os
from core.crypto import CryptoEngine
from core.fragmentation import fragment_message
from core.key_schedule import derive_layer_keys
from core.time_lock import TimeLock

def generate_traffic(agent, message, dummy_ratio):
    timelock = TimeLock(ttl_ms=30)  # 30 ms hard deadline
seal = timelock.seal(nonce)
agent.last_timelock = seal
    crypto = CryptoEngine()
    nonce = os.urandom(16)

    agent.last_nonce = nonce
    keys = derive_layer_keys(agent.master_key, nonce)

    # ---- IMPORTANT FIX ----
    if message is None:
        # Idle traffic: indistinguishable dummy-only flow
        data = os.urandom(32)
    else:
        data = message

    for k in keys:
        data = crypto.encrypt(data, k)

    packets = fragment_message(
        data,
        n_fragments=agent.fragment_count,
        dummy_ratio=dummy_ratio
    )

    agent.expected_real_fragments = sum(not p.is_dummy for p in packets)
    return packets
