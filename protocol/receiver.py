def receive_and_reconstruct(packets, agent):
    if agent.is_locked() or not packets:
        return False

    valid = 0

    for p in packets:
        if not p.is_dummy:
            valid += 1

    return valid >= agent.threshold
