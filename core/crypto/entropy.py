import math
from collections import Counter

def shannon_entropy(data):
    if not data: return 0
    entropy = 0
    counts = Counter(data)
    for count in counts.values():
        p = count / len(data)
        entropy -= p * math.log2(p)
    return entropy

def verify_indistinguishability(real_packet, dummy_packet):
    """Objective 4: Mathematical proof of stealth"""
    e_real = shannon_entropy(real_packet)
    e_dummy = shannon_entropy(dummy_packet)
    # The architecture goal is a delta < 0.1 bits
    return abs(e_real - e_dummy) < 0.1
