"""Channel loss models (seeded, numpy Generator).

Bernoulli(p):            each packet lost independently with probability p.
GilbertElliott(...):     two-state Markov chain. States G (good) and B (bad);
                         P(G->B) = p_gb, P(B->G) = p_bg; loss prob h_G in G, h_B in B.
                         Stationary P(B) = p_gb / (p_gb + p_bg); mean loss
                         = π_G h_G + π_B h_B; mean burst (sojourn in B) = 1/p_bg.
                         (Gilbert 1960; Elliott 1963.)  The chain state persists
                         across packets *and* across messages.
from_mean_burst(loss, burst): Gilbert model (h_G=0, h_B=1) with the given mean
                         loss rate and mean burst length.
"""
import numpy as np


class Bernoulli:
    def __init__(self, p, rng):
        self.p, self.rng = float(p), rng

    def lost(self, n):
        return self.rng.random(n) < self.p

    @property
    def mean_loss(self):
        return self.p


class GilbertElliott:
    def __init__(self, p_gb, p_bg, h_g, h_b, rng):
        self.p_gb, self.p_bg, self.h_g, self.h_b, self.rng = p_gb, p_bg, h_g, h_b, rng
        pib = p_gb / (p_gb + p_bg) if (p_gb + p_bg) > 0 else 0.0
        self.bad = rng.random() < pib            # start in stationary distribution

    @classmethod
    def from_mean_burst(cls, loss, burst, rng):
        if loss <= 0:
            return cls(0.0, 1.0, 0.0, 1.0, rng)
        p_bg = 1.0 / burst
        p_gb = loss * p_bg / (1.0 - loss)
        return cls(p_gb, p_bg, 0.0, 1.0, rng)

    @property
    def mean_loss(self):
        pib = self.p_gb / (self.p_gb + self.p_bg)
        return (1 - pib) * self.h_g + pib * self.h_b

    def lost(self, n):
        if self.h_g == 0.0 and self.h_b == 1.0:
            return self._lost_runs(n)
        return self._lost_steps(n)

    def _lost_runs(self, n):
        """Exact sampling for the Gilbert case via geometric sojourn times
        (sojourn in G ~ Geom(p_gb), in B ~ Geom(p_bg), both on {1,2,...}).
        The current sojourn is memoryless, so restarting it at each call is exact."""
        if self.p_gb == 0.0 and not self.bad:
            return np.zeros(n, dtype=bool)
        out, filled, state = np.empty(n, dtype=bool), 0, self.bad
        while filled < n:
            m = max(16, int((n - filled) * min(self.p_gb, self.p_bg) * 2) + 16)
            lens_g = self.rng.geometric(self.p_gb, m) if self.p_gb > 0 else np.full(m, n + 1)
            lens_b = self.rng.geometric(self.p_bg, m)
            seq = np.empty(2 * m, dtype=np.int64)
            vals = np.empty(2 * m, dtype=bool)
            if state:
                seq[0::2], seq[1::2] = lens_b, lens_g; vals[0::2], vals[1::2] = True, False
            else:
                seq[0::2], seq[1::2] = lens_g, lens_b; vals[0::2], vals[1::2] = False, True
            chunk = np.repeat(vals, seq)
            take = min(n - filled, chunk.size)
            out[filled:filled + take] = chunk[:take]
            filled += take
            if take < chunk.size:
                # truncated inside a run: next packet's state by one Markov step
                last = bool(out[filled - 1])
                u = self.rng.random()
                self.bad = (u >= self.p_bg) if last else (u < self.p_gb)
                return out
            state = not bool(out[filled - 1])     # chunk ended exactly at a run boundary
        self.bad = state                          # next packet starts the opposite run
        return out

    def _lost_steps(self, n):
        out = np.empty(n, dtype=bool)
        u = self.rng.random((n, 2))
        for i in range(n):
            out[i] = u[i, 0] < (self.h_b if self.bad else self.h_g)
            self.bad = (u[i, 1] >= self.p_bg) if self.bad else (u[i, 1] < self.p_gb)
        return out


class Multipath:
    """Fragments alternate over independent paths (round robin)."""

    def __init__(self, paths):
        self.paths = paths

    def lost(self, n):
        out = np.empty(n, dtype=bool)
        per = [np.flatnonzero(np.arange(n) % len(self.paths) == j) for j in range(len(self.paths))]
        for j, idx in enumerate(per):
            out[idx] = self.paths[j].lost(len(idx))
        return out

    @property
    def mean_loss(self):
        return float(np.mean([p.mean_loss for p in self.paths]))
