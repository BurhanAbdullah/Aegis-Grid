from core.key_schedule import derive_single_key

class SecureAgent:
    ALPHA = 0.85
    THETA = 0.35

    N_MIN = 5
    N_MAX = 30
    N_DEFAULT = 12

    RHO_MIN = 0.5
    RHO_MAX = 3.0
    RHO_DEFAULT = 1.5

    def __init__(self, master_key: bytes):
        self.master_key = master_key
        self.cap = 0.0
        self.fragment_count = self.N_DEFAULT
        self.dummy_ratio = self.RHO_DEFAULT

    def observe(self, error: float):
        self.cap = self.ALPHA * self.cap + error

        if self.cap >= self.THETA:
            self.fragment_count = max(self.N_MIN, self.fragment_count - 1)
            self.dummy_ratio = max(self.RHO_MIN, self.dummy_ratio - 0.1)

    def get_layer_key(self, layer: int) -> bytes:
        return derive_single_key(self.master_key, layer)
