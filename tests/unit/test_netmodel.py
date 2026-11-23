import numpy as np
from aegis_pq.netmodel import Bernoulli, GilbertElliott, Multipath


def test_bernoulli_rate():
    rng = np.random.default_rng(1)
    assert abs(Bernoulli(0.1, rng).lost(200000).mean() - 0.1) < 0.003


def test_gilbert_mean_loss_and_burst_length():
    rng = np.random.default_rng(2)
    ch = GilbertElliott.from_mean_burst(0.1, 5.0, rng)
    x = ch.lost(400000)
    assert abs(x.mean() - 0.1) < 0.01
    # mean run length of consecutive losses ≈ 5
    runs, r = [], 0
    for v in x:
        if v: r += 1
        elif r: runs.append(r); r = 0
    assert abs(np.mean(runs) - 5.0) < 0.3


def test_gilbert_is_bursty_not_iid():
    rng = np.random.default_rng(3)
    x = GilbertElliott.from_mean_burst(0.1, 8.0, rng).lost(200000)
    p_loss_after_loss = x[1:][x[:-1]].mean()
    assert p_loss_after_loss > 0.8          # i.i.d. would give ≈ 0.1


def test_multipath_interleaves():
    rng = np.random.default_rng(4)
    mp = Multipath([Bernoulli(1.0, rng), Bernoulli(0.0, rng)])
    x = mp.lost(10)
    assert x.tolist() == [True, False] * 5


def test_run_sampler_matches_step_sampler():
    """The fast geometric-run sampler must match the per-step Markov simulation
    (window success statistics, used by EXP-003)."""
    import numpy as np
    stats = []
    for fast in (True, False):
        rng = np.random.default_rng(11)
        ch = GilbertElliott.from_mean_burst(0.1, 4.0, rng)
        f = ch._lost_runs if fast else ch._lost_steps
        wins = np.array([f(10).sum() for _ in range(40000)])
        stats.append(((wins == 0).mean(), wins.mean(), (wins >= 5).mean()))
    (a0, a1, a2), (b0, b1, b2) = stats
    assert abs(a0 - b0) < 0.012 and abs(a1 - b1) < 0.03 and abs(a2 - b2) < 0.01
