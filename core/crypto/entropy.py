import math
from collections import Counter

def shannon_entropy(data: bytes) -> float:
    counts = Counter(data)
    total = len(data)
    entropy = 0.0
    for c in counts.values():
        p = c / total
        entropy -= p * math.log2(p)
    return entropy

def verify_stealth(b1: bytes, b2: bytes, delta: float = 0.1) -> bool:
    """
    Shannon indistinguishability test:
    |H(b1) - H(b2)| < delta
    """
    return abs(shannon_entropy(b1) - shannon_entropy(b2)) < delta
