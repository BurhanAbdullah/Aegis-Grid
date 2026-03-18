import hashlib
from core.key_schedule import derive_single_key
import os

class SecureAgent:
    ALPHA         = 0.85
    THETA         = 0.35
    LOCKOUT_LIMIT = 1.0
    CAP_MAX       = 1.0
    N_MIN         = 5
    N_MAX         = 30
    N_DEFAULT     = 12
    RHO_MIN       = 0.5
    RHO_MAX       = 3.0
    RHO_DEFAULT   = 1.5

    def __init__(self, master_key: bytes):
        self.master_key      = master_key
        self._nonce          = os.urandom(16)
        self.locked          = False
        self.cap             = 0.0
        self._step           = 0
        self.fragment_count  = self.N_DEFAULT
        self.dummy_ratio     = self.RHO_DEFAULT
        self.threshold       = self.N_DEFAULT + 1
        self._lock_announced = False

    def _update_cap(self, e_k):
        self.cap = min(self.CAP_MAX, self.ALPHA * self.cap + e_k)
        self._step += 1

    def add_attack_pressure(self, amount=1.0):
        if self.locked: return
        self._update_cap(amount * 0.15)
        self._adapt()
        if self.cap >= self.LOCKOUT_LIMIT:
            self._lockout()

    def observe(self, loss):
        if self.locked: return
        self._update_cap(loss * 0.10)
        self._adapt()

    def _adapt(self):
        if self.cap < self.THETA: return
        r = min(1.0, self.cap / self.LOCKOUT_LIMIT)
        self.fragment_count = max(self.N_MIN, min(self.N_MAX, int(self.N_DEFAULT + r * (self.N_MAX - self.N_DEFAULT))))
        self.dummy_ratio    = max(self.RHO_MIN, min(self.RHO_MAX, self.RHO_DEFAULT + r * (self.RHO_MAX - self.RHO_DEFAULT)))
        self.threshold      = self.fragment_count + 1

    def _lockout(self):
        self.locked = True
        if not self._lock_announced:
            self._lock_announced = True
            print(f"[L6-CAP] LOCKOUT -> CAP={self.cap:.3f} at step {self._step}")

    def is_locked(self): return self.locked

    def get_layer_key(self, layer_id):
        return derive_single_key(self.master_key, self._nonce, layer_id)

    def state(self):
        return {"cap": round(self.cap,4), "step": self._step, "locked": self.locked,
                "fragment_count": self.fragment_count, "dummy_ratio": round(self.dummy_ratio,3),
                "threshold": self.threshold}
