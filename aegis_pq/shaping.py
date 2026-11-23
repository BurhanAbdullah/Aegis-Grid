"""Constant-rate, constant-size traffic shaper (AGP/1 layer L3).

At every tick (period Δ) exactly one fixed-size AEAD record is emitted: the
real fragment with the earliest absolute deadline (EDF) if one is queued,
otherwise an encrypted dummy. Fragments whose deadline has passed before they
can be sent are dropped (fail-secure: late data is never sent).

What this hides from a passive observer, and what it does not, is measured in
EXP-005; it is not assumed. The shaper hides *when* and *how much* real data is
sent only if the tick schedule and record size are independent of the data;
implementation timing differences (e.g. sealing a real vs a dummy record) are
measured, not ruled out. Queueing at Δ adds delay; that cost is also measured.
"""
import heapq
import itertools
import os

from .channel import SecureChannel, TYPE_DATA, TYPE_DUMMY, INNER


class ConstantRateShaper:
    def __init__(self, chan: SecureChannel, period_ms: float):
        if not chan.cfg.body_size:
            raise ValueError("shaping requires a fixed record body size")
        self.chan, self.period_ms = chan, float(period_ms)
        self._q = []                                  # (abs_deadline, seq, payload, t_gen, rel_deadline, tag)
        self._seq = itertools.count()
        self.stats = {"ticks": 0, "real": 0, "dummy": 0, "dropped_late": 0}
        self.dropped = []                             # tags of dropped fragments

    def enqueue(self, payload: bytes, t_gen_ms: float, deadline_ms: float, tag=None):
        heapq.heappush(self._q, (t_gen_ms + deadline_ms, next(self._seq), payload, t_gen_ms, deadline_ms, tag))

    def __len__(self):
        return len(self._q)

    def tick(self, now_ms: float):
        """Return (record, tag) where tag is None for a dummy."""
        self.stats["ticks"] += 1
        while self._q and self._q[0][0] < now_ms:
            item = heapq.heappop(self._q)
            self.stats["dropped_late"] += 1
            self.dropped.append(item[5])
        if self._q:
            _, _, payload, t_gen, dl, tag = heapq.heappop(self._q)
            self.stats["real"] += 1
            return self.chan.seal(payload, dl, TYPE_DATA, t_gen), tag
        self.stats["dummy"] += 1
        size = self.chan.cfg.body_size - INNER.size
        return self.chan.seal(os.urandom(size), 1e3, TYPE_DUMMY), None
