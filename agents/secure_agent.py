import hashlib

class SecureAgent:
    PRESSURE_LIMIT = 5.5

    def __init__(self, master_key):
        self.master_key = master_key
        self.locked = False
        self.pressure = 0.0
        self._lock_announced = False

        # Required protocol contract
        self.base_fragments = 12
        self.fragment_count = 12
        self.threshold = 12

    def get_layer_key(self, layer_id):
        return hashlib.sha256(
            self.master_key + str(layer_id).encode()
        ).digest()

    def is_locked(self):
        return self.locked

    def observe(self, loss):
        if self.locked:
            return

        # Adaptive quorum (availability)
        self.threshold = max(4, int(self.base_fragments * (1.0 - loss)))

    def add_attack_pressure(self, amount):
        if self.locked:
            return

        self.pressure += amount
        if self.pressure >= self.PRESSURE_LIMIT:
            self.locked = True
            if not self._lock_announced:
                print(f"[SECURITY] TIME-LOCK irreversible failure -> Pressure: {self.pressure:.2f}")
                self._lock_announced = True
