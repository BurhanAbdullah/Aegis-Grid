from core.timing import within_time_window
from core.time_lock import TimeLock

def receive_and_reconstruct(packets, agent, time_window_ms=30):
    timelock = TimeLock(ttl_ms=30)
if not timelock.verify(agent.last_nonce, agent.last_timelock):
    agent.locked = True
    return None

    if agent.locked:
        return None

    valid = []
    for p in packets:
        if not within_time_window(p.timestamp, time_window_ms):
            agent.locked = True
            return None
        if not p.is_dummy:
            valid.append(p)

    # -----------------------------
    # Threshold-based reconstruction
    # -----------------------------
    required = agent.expected_real_fragments
    received = len(valid)

    # Require at least 60% fragments
    if received < 0.6 * required:
        return None

    # Simulate reconstruction success
    payload = b"".join(p.payload for p in valid)
    return payload
