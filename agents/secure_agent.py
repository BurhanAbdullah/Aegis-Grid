import random

class SecureAgent:
    def __init__(self, master_key):
        self.master_key = master_key
        self.threat_score = 0.0
        self.packet_budget = 50
        self.fragment_count = 8
        self.last_nonce = None

    def update(self, loss, delay):
        self.threat_score = min(1.0, loss + delay)
        self.fragment_count = 8 + int(self.threat_score * 4)

    def secret_positions(self, n):
        rng = random.Random(int.from_bytes(self.master_key[:4], 'big'))
        return rng.sample(range(self.packet_budget), n)
