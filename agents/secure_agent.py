import hashlib

class SecureAgent:
    """V1: Baseline Adaptive Agent (Classical Cryptography)"""
    PRESSURE_LIMIT = 5.5
    def __init__(self, master_key):
        self.master_key = master_key
        self.locked = False
        self.pressure = 0.0
        self.fragment_count = 12 
        self.threshold = 12

    def is_locked(self):
        return self.locked

    def observe(self, loss):
        if self.locked: return
        self.threshold = max(4, int(self.fragment_count * (1.0 - loss)))

    def add_attack_pressure(self, amount):
        if self.locked: return
        self.pressure += amount
        if self.pressure >= self.PRESSURE_LIMIT:
            self.locked = True
            print(f"[V1-SECURITY] LOCKOUT TRIGGERED -> Pressure: {self.pressure:.2f}")

    def get_layer_key(self, layer_id):
        return hashlib.sha256(self.master_key + str(layer_id).encode()).digest()
