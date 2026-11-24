"""Attack-pressure statistics and the bounded adaptation policy (AGP/1 layer L6).

Observables per epoch k (all computable by the receiver from authenticated
records and sequence numbers; nothing requires ground truth):
    o1 = fraction of expected fragments missing (sequence gaps)
    o2 = fraction of messages that missed their deadline or were not reconstructed
    o3 = rejected records per expected record (AUTH_FAIL, REPLAY, MALFORMED, ...)

Normalisation (fitted on benign calibration data only):
    z_jk = (o_jk − μ_j) / max(σ_j, σ_floor_j)
Event score:
    e_k = (1/J) Σ_j max(0, z_jk)                          (one-sided, ≥ 0)
Cumulative attack pressure (the manuscript's Eq. (14), retained):
    CAP_k = α · CAP_{k−1} + e_k ,   0 ≤ α < 1,  alarm when CAP_k ≥ θ.

ANALYTICALLY DERIVED: CAP_k = EWMA_k / (1−α) with EWMA_k = α EWMA_{k−1} + (1−α) e_k.
CAP is therefore an EWMA control chart (Roberts 1959) on the aggregated score
e_k with threshold θ(1−α); it is not a new detector. What the architecture adds
is the bounded, hysteretic action policy below, evaluated against baselines.

Baselines: Shewhart (fixed threshold on e_k), per-observable EWMA with OR
combination (Roberts 1959), CUSUM on e_k (Page 1954).
"""
import numpy as np


class Normaliser:
    def __init__(self, benign_obs: np.ndarray, floor):
        self.mu = benign_obs.mean(0)
        self.sd = np.maximum(benign_obs.std(0), np.asarray(floor, float))

    def z(self, o):
        return (np.asarray(o, float) - self.mu) / self.sd

    def score(self, o):
        return float(np.maximum(0.0, self.z(o)).mean())


class CAP:
    name = "CAP"

    def __init__(self, norm, theta, alpha=0.85):
        self.norm, self.theta, self.alpha, self.s = norm, theta, alpha, 0.0

    def reset(self):
        self.s = 0.0

    def update(self, o):
        self.s = self.alpha * self.s + self.norm.score(o)
        return self.s >= self.theta


class Shewhart:
    name = "Shewhart"

    def __init__(self, norm, theta):
        self.norm, self.theta = norm, theta

    def reset(self):
        pass

    def update(self, o):
        return self.norm.score(o) >= self.theta


class EWMAPerFeature:
    name = "EWMA"

    def __init__(self, norm, theta, lam=0.2):
        self.norm, self.theta, self.lam = norm, theta, lam
        self.s = np.zeros_like(norm.mu)

    def reset(self):
        self.s = np.zeros_like(self.norm.mu)

    def update(self, o):
        self.s = self.lam * self.norm.z(o) + (1 - self.lam) * self.s
        return bool((self.s >= self.theta).any())


class CUSUM:
    name = "CUSUM"

    def __init__(self, norm, theta, kappa=0.5):
        self.norm, self.theta, self.kappa, self.s = norm, theta, kappa, 0.0

    def reset(self):
        self.s = 0.0

    def update(self, o):
        self.s = max(0.0, self.s + self.norm.score(o) - self.kappa)
        return self.s >= self.theta


class Never:
    name = "static"

    def __init__(self, *a, **k):
        pass

    def reset(self):
        pass

    def update(self, o):
        return False


class AdaptationPolicy:
    """Two-level policy over the admissible set Ψ = {(k, n_normal), (k, n_protect)}.

    Enter PROTECT on an alarm; return to NORMAL only after `hold` consecutive
    alarm-free epochs (hysteresis). k, the record size and the shaping period
    never change, so the capture threshold (k shards) and the observable
    traffic shape are invariant under adaptation.
    """

    def __init__(self, detector, k=5, n_normal=7, n_protect=10, hold=8):
        if not (1 <= k <= n_normal <= n_protect):
            raise ValueError("inadmissible parameter set")
        self.d, self.k, self.levels, self.hold = detector, k, (n_normal, n_protect), hold
        self.mode, self.quiet = 0, 0

    def reset(self):
        self.d.reset(); self.mode, self.quiet = 0, 0

    @property
    def n(self):
        return self.levels[self.mode]

    def step(self, o):
        alarm = self.d.update(o)
        if alarm:
            self.mode, self.quiet = 1, 0
        elif self.mode == 1:
            self.quiet += 1
            if self.quiet >= self.hold:
                self.mode, self.quiet = 0, 0
        return alarm
