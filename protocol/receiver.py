from core.timing import within_time_window

def receive_and_reconstruct(packets, agent, time_window_ms=30):
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
