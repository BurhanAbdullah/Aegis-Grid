class SecureAgent:
    def __init__(self, master_key):
        self.master_key = master_key

        # Fragment parameters
        self.base_fragments = 12
        self.fragment_count = 12
        self.threshold = 12

        # Security policy
        self.max_invalid_ratio = 0.35
        self.max_replay_ratio = 0.40

        # State
        self.locked = False

    # Phase 2: no adaptive time-based behavior
    def observe(self, loss):
        return

    # Phase 2 compatibility shim
    def is_locked(self):
        return self.locked

    # Phase 2 compatibility shim (no time-lock)
    def add_attack_pressure(self, weight):
        pass
