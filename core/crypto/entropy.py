import math
from collections import Counter
def shannon_entropy(data):
    if not data: return 0
    counts = Counter(data)
    return -sum((c/len(data)) * math.log2(c/len(data)) for c in counts.values())
def verify_stealth(p1, p2):
    return abs(shannon_entropy(p1) - shannon_entropy(p2)) < 0.1
