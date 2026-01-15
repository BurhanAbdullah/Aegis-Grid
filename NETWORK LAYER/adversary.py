import random

def apply_attacks(packets, drop_rate=0.0, delay=False):
    out = []
    for p in packets:
        if random.random() < drop_rate:
            continue
        if delay:
            p.timestamp += random.uniform(0.01, 0.05)
        out.append(p)
    return out
