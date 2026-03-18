import hashlib
from core.key_schedule import derive_single_key
import os


class SecureAgent:
    """
    Aegis-Grid Adaptive Security Agent — L6.

    Implements the CAP (Cumulative Attack Pressure) metric from Equation 14:

        CAP_k = α · CAP_{k-1} + e_k

    where:
        α = 0.85   exponential decay factor (prevents indefinite accumulation)
        e_k ≥ 0   pressure event at step k (latency violation, loss, forgery)
        θ = 0.35   threshold above which parameter tightening is triggered

    When CAP_k ≥ θ, the agent tightens N, ρ, λ within the admissible
    region Θ to restore structural invariants (Proposition 4).

    When CAP_k ≥ LOCKOUT_LIMIT, the agent locks the node entirely (L7 fallback).

    This replaces the previous hardcoded PRESSURE_LIMIT = 5.5 accumulator
    which had no decay, diverged under sustained attack, and did not match
    the paper's formal model.
    """

    # ── CAP parameters (matching paper Table 2 / Equation 14) ────────────────
    ALPHA         = 0.85    # exponential decay factor
    THETA         = 0.35    # adaptation trigger threshold
    LOCKOUT_LIMIT = 1.0     # full lockout threshold (normalised CAP)
    CAP_MAX       = 1.0     # normalised cap ceiling

    # ── Protocol parameters (admissible region Θ) ────────────────────────────
    N_MIN         = 5
    N_MAX         = 30
    N_DEFAULT     = 12
    RHO_MIN       = 0.5
    RHO_MAX       = 3.0
    RHO_DEFAULT   = 1.5

    def __init__(self, master_key: bytes):
        self.master_key     = master_key
        self._nonce         = os.urandom(16)   # per-session nonce for HKDF
        self.locked         = False

        # CAP state
        self.cap            = 0.0              # CAP_k (normalised 0..1)
        self._step          = 0

        # Adaptive parameters (start at defaults, agent adjusts)
        self.fragment_count = self.N_DEFAULT
        self.dummy_ratio    = self.RHO_DEFAULT
        self.threshold      = self.N_DEFAULT + 1  # reconstruction quorum (N real + 1 AONT key block)

        # Logging
        self._lock_announced = False

    # ── Core CAP update — Equation 14 ────────────────────────────────────────
    def _update_cap(self, e_k: float):
        """
        CAP_k = α · CAP_{k-1} + e_k   (Eq. 14)
        Clipped to [0, CAP_MAX] to keep it normalised.
        """
        self.cap = min(
            self.CAP_MAX,
            self.ALPHA * self.cap + e_k
        )
        self._step += 1

    # ── Pressure events (e_k values matching paper Section 3.6) ──────────────
    def add_attack_pressure(self, amount: float = 1.0):
        """
        Register an adversarial event (forgery, replay, integrity failure).
        Triggers adaptation if CAP crosses θ; triggers lockout if CAP → 1.0.
        """
        if self.locked:
            return
        self._update_cap(amount * 0.15)   # scale raw event to normalised range
        self._adapt()
        if self.cap >= self.LOCKOUT_LIMIT:
            self._lockout()

    def observe(self, loss: float):
        """
        Register a network loss observation.
        loss ∈ [0, 1] — fraction of packets lost in this window.
        Updates CAP and adapts parameters to maintain invariants.
        """
        if self.locked:
            return
        e_k = loss                         # loss directly enters CAP as e_k
        self._update_cap(e_k * 0.10)
        self._adapt()

    # ── Adaptive policy — preserves invariants within Θ ──────────────────────
    def _adapt(self):
        """
        If CAP_k ≥ θ, tighten N and ρ to restore structural invariants.
        All adjustments stay within admissible region Θ (Proposition 4).
        """
        if self.cap < self.THETA:
            return

        # Pressure above threshold → increase N (more fragments = more resilience)
        # and increase ρ (more dummies = better traffic indistinguishability)
        pressure_ratio = min(1.0, self.cap / self.LOCKOUT_LIMIT)

        new_n = int(
            self.N_DEFAULT + pressure_ratio * (self.N_MAX - self.N_DEFAULT)
        )
        new_rho = (
            self.RHO_DEFAULT + pressure_ratio * (self.RHO_MAX - self.RHO_DEFAULT)
        )

        # Clamp within Θ
        self.fragment_count = max(self.N_MIN, min(self.N_MAX, new_n))
        self.dummy_ratio    = max(self.RHO_MIN, min(self.RHO_MAX, new_rho))
        self.threshold      = self.fragment_count + 1  # N + 1 (AONT key block)

    # ── Lockout (L7 fail-secure trigger) ─────────────────────────────────────
    def _lockout(self):
        self.locked = True
        if not self._lock_announced:
            self._lock_announced = True
            print(
                f"[L6-CAP] LOCKOUT → CAP={self.cap:.3f} ≥ {self.LOCKOUT_LIMIT} "
                f"at step {self._step}"
            )

    def is_locked(self) -> bool:
        return self.locked

    # ── Key derivation — now uses HKDF via key_schedule ──────────────────────
    def get_layer_key(self, layer_id: int) -> bytes:
        """
        Derive per-layer key using HKDF (RFC 5869).
        Replaces previous SHA-256(master || layer_id) which lacked domain sep.
        """
        return derive_single_key(self.master_key, self._nonce, layer_id)

    # ── State inspection (for simulation logging) ─────────────────────────────
    def state(self) -> dict:
        return {
            "cap":            round(self.cap, 4),
            "step":           self._step,
            "locked":         self.locked,
            "fragment_count": self.fragment_count,
            "dummy_ratio":    round(self.dummy_ratio, 3),
            "threshold":      self.threshold,
        }
