class SecureAgent:
    def __init__(self, key):
        self.master_key = key
        self.base_fragments = 12
        self.fragment_count = 12
        self.threshold = 12
        self.locked = False
    def observe(self, loss):
        self.threshold = max(3, int(self.base_fragments * (1.0 - loss)))
    def is_locked(self):
        return self.locked