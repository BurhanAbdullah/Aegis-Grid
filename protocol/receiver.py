from core.timing import within_time_window

def receive_and_reconstruct(packets, agent, time_window_ms=50):
    """
    Receiver-side reconstruction with strict security:
    - Time-bounded validity
    - Dummy filtering
    - Threshold-based reconstruction
    """

    # Reject immediately if no packets
    if not packets:
        return None

    # Time-bounded check
    now_valid = []
    for p in packets:
        if within_time_window(p.timestamp, time_window_ms):
            now_valid.append(p)

    if not now_valid:
        return None

    # Extract real fragments
    real_packets = [p for p in now_valid if not p.is_dummy]

    # SECURITY RULE:
    # Require at least 70% of expected real fragments
    required = int(0.7 * agent.expected_real_fragments)

    if len(real_packets) < required:
        return None

    # Reconstruction succeeds (payload content irrelevant for experiment)
    reconstructed = b''.join(p.payload for p in real_packets)
    return reconstructed
