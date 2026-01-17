import hashlib

class SecureAgent:
    PRESSURE_LIMIT = 5.0

    def __init__(self, master_key):
        self.master_key = master_key
        self.locked = False
        self.pressure = 0.0

        # Fragment / quorum control (Pillar 1)
        self.base_fragments = 12
        self.fragment_count = 12
        self.threshold = 12

    # ---------- Required by protocol ----------
    def is_locked(self):
        return self.locked

    def add_attack_pressure(self, amount):
        if self.locked:
            return
        self.pressure += amount
        if self.pressure >= self.PRESSURE_LIMIT:
            self.locked = True

    # ---------- Pillar logic ----------
    def get_layer_key(self, layer_id):
        """Pillar 1: per-layer key separation"""
        return hashlib.sha256(
            self.master_key + str(layer_id).encode()
        ).digest()

    def observe(self, loss, forgery_detected=False):
        """Pillar 2 & 3: cumulative pressure + time-lock"""
        if self.locked:
            return

        # DDoS / packet loss signal
        self.pressure += loss * 2.0

        # Forgery escalation
        if forgery_detected:
            self.pressure += 2.5

        # Adaptive quorum (Pillar 1)
        self.threshold = max(4, int(self.base_fragments * (1.0 - loss)))

        # Irreversible lock
        if self.pressure >= self.PRESSURE_LIMIT:
            self.locked = True
