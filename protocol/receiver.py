from core.signature import SignatureEngine

def receive_and_reconstruct(packets, agent):
    if agent.is_locked() or not packets:
        return False

    verifier = SignatureEngine()
    seen = set()

    for p in packets:
        key = agent.get_layer_key(p.frag_id)
        if verifier.verify(p.signable(), p.signature, key):
            seen.add(p.frag_id)
        else:
            agent.add_attack_pressure(1.5)

    return len(seen) >= agent.threshold
