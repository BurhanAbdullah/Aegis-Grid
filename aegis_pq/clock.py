"""Clocks.  Protocol code never calls time.* directly so tests can inject time."""
import time


class SystemClock:
    """Wall-clock milliseconds since the epoch (for deadlines carried on the wire)
    and a monotonic nanosecond counter (for local durations)."""

    def now_ms(self) -> float:
        return time.time_ns() / 1e6

    def mono_ns(self) -> int:
        return time.perf_counter_ns()


class ManualClock:
    """Deterministic clock for tests and discrete-event simulation."""

    def __init__(self, t_ms: float = 1_700_000_000_000.0):
        self.t_ms = float(t_ms)

    def now_ms(self) -> float:
        return self.t_ms

    def mono_ns(self) -> int:
        return int(self.t_ms * 1e6)

    def advance(self, ms: float) -> None:
        self.t_ms += ms
