from core.signature import SignatureEngine

def receive_and_reconstruct(packets, agent):
    if agent.is_locked() or not packets: return False
    
    v = SignatureEngine()
    seen, forgeries = set(), 0
    
    for p in packets:
        # Pillar 3: Integrity Check
        if v.verify(p.signable(), p.signature, agent.master_key):
            seen.add(p.frag_id)
        else:
            forgeries += 1
            agent.add_attack_pressure(1.5) # Permanent damage per forgery

    # Pillar 2: DDoS Pressure Check
    if len(packets) < (agent.fragment_count * 0.5):
        agent.add_attack_pressure(0.1) # Soft damage for sustained loss
        
    return len(seen) >= agent.threshold
