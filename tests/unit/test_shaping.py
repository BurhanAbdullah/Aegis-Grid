from aegis_pq.channel import ChannelConfig, SecureChannel, TYPE_DUMMY, TYPE_DATA
from aegis_pq.handshake import Initiator, Responder, run_handshake
from aegis_pq.pipeline import Sender, body_size_for
from aegis_pq.shaping import ConstantRateShaper
import pytest


def _pair(pki, clock, body):
    ca, creds = pki
    i = Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock)
    r = Responder("rtu-07", creds["rtu-07"], ca.cert, clock)
    ki, kr = run_handshake(i, r)
    cfg = ChannelConfig(body_size=body)
    return SecureChannel(ki, clock, cfg), SecureChannel(kr, clock, cfg)


def test_requires_fixed_size(pki, clock):
    a, _ = _pair(pki, clock, 0)
    with pytest.raises(ValueError):
        ConstantRateShaper(a, 2.0)


def test_one_constant_size_record_per_tick_and_dummies(pki, clock):
    body = body_size_for(128, 5)
    a, b = _pair(pki, clock, body)
    sh, snd = ConstantRateShaper(a, 2.0), Sender(a, 5, 7)
    _, frags = snd.fragment(b"x" * 100)
    for f in frags:
        sh.enqueue(f, clock.now_ms(), 100.0, tag="m")
    sizes, types = set(), []
    for _ in range(12):
        rec, tag = sh.tick(clock.now_ms())
        sizes.add(len(rec)); types.append(b.open(rec)[0])
        clock.advance(2.0)
    assert len(sizes) == 1
    assert types[:7] == [TYPE_DATA] * 7 and types[7:] == [TYPE_DUMMY] * 5
    assert sh.stats == {"ticks": 12, "real": 7, "dummy": 5, "dropped_late": 0}


def test_edf_order_and_late_drop(pki, clock):
    a, b = _pair(pki, clock, body_size_for(16, 1))
    sh = ConstantRateShaper(a, 2.0)
    t = clock.now_ms()
    sh.enqueue(b"slow", t, 50.0, "slow")
    sh.enqueue(b"fast", t, 5.0, "fast")
    sh.enqueue(b"late", t, 1.0, "late")
    clock.advance(3.0)                        # 'late' deadline passed before first tick
    rec, tag = sh.tick(clock.now_ms())
    assert tag == "fast" and b.open(rec)[1] == b"fast"
    rec, tag = sh.tick(clock.now_ms())
    assert tag == "slow"
    assert sh.dropped == ["late"] and sh.stats["dropped_late"] == 1
