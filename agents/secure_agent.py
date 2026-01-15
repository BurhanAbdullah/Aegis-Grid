class SecureAgent:
    def __init__(self, master_key):
        self.master_key = master_key

        # Threat and adaptation
        self.threat_score = 0.0

        # Fragment tracking
        self.fragment_count = 8
        self.expected_real_fragments = 0

        # Security state
        self.last_nonce = None
        self.locked = False   # ✅ REQUIRED

    def update(self, loss, delay):
        self.threat_score = min(1.0, 0.7 * self.threat_score + 0.3 * (loss + delay))

        # Adaptive behavior
        self.fragment_count = 8 + int(4 * self.threat_score)

    def decide_dummy_ratio(self):
        return 1.0 + 2.0 * self.threat_score
