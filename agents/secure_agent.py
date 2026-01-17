class SecureAgent:
    def __init__(self, key=None):
        self.master_key = key
        self.locked = False
        self.attack_pressure = 0.0
        
        # Pillars 1 & 2: Adaptive Parameters
        self.base_fragments = 12
        self.fragment_count = 12
        self.threshold = 12
        
        # Pillar 3: Permanent Failure Limit
        self.PRESSURE_LIMIT = 5.0

    def observe(self, loss_rate):
        """Pillar 2: DDoS Pressure Feedback"""
        # If loss is high, agent becomes more 'forgiving' to maintain power
        # but raises strictness if forgery is detected.
        self.threshold = max(4, int(self.base_fragments * (1.0 - loss_rate)))

    def add_attack_pressure(self, weight):
        """Pillar 3: Cumulative Attack Pressure"""
        if self.locked: return
        self.attack_pressure += weight
        if self.attack_pressure >= self.PRESSURE_LIMIT:
            self.locked = True
            print("[SECURITY] TIME-LOCK irreversible failure triggered.")

    def is_locked(self): return self.locked
