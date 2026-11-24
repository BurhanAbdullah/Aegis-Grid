import numpy as np
import pytest
from aegis_pq.detectors import Normaliser, CAP, Shewhart, EWMAPerFeature, CUSUM, AdaptationPolicy


def _norm():
    rng = np.random.default_rng(1)
    return Normaliser(rng.normal([0.01, 0.0, 0.0], [0.005, 0.001, 0.001], (500, 3)), [1e-3] * 3)


def test_score_is_nonnegative_and_one_sided():
    n = _norm()
    assert n.score(n.mu - 10 * n.sd) == 0.0
    assert n.score(n.mu + 3 * n.sd) == pytest.approx(3.0)


def test_cap_equals_scaled_ewma():
    n, a = _norm(), 0.85
    cap, ew = CAP(n, 1e9, a), 0.0
    rng = np.random.default_rng(2)
    for _ in range(200):
        o = n.mu + rng.normal(0, 2, 3) * n.sd
        cap.update(o)
        ew = a * ew + (1 - a) * n.score(o)
        assert cap.s == pytest.approx(ew / (1 - a))


def test_detectors_alarm_on_step_and_not_on_mean():
    n = _norm()
    for D in (CAP(n, 3.0), Shewhart(n, 2.0), EWMAPerFeature(n, 1.0), CUSUM(n, 3.0)):
        assert not any(D.update(n.mu) for _ in range(50))
        assert any(D.update(n.mu + 5 * n.sd) for _ in range(10))


def test_policy_hysteresis_and_invariants():
    n = _norm()
    p = AdaptationPolicy(Shewhart(n, 2.0), k=5, n_normal=7, n_protect=10, hold=3)
    assert p.n == 7
    p.step(n.mu + 5 * n.sd); assert p.n == 10
    for _ in range(2):
        p.step(n.mu); assert p.n == 10
    p.step(n.mu); assert p.n == 7
    assert p.k == 5
    with pytest.raises(ValueError):
        AdaptationPolicy(Shewhart(n, 1), k=8, n_normal=7)
