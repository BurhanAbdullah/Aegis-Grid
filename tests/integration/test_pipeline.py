"""End-to-end: handshake -> AONT -> RS -> fixed-size records -> receiver."""
import os, random
import pytest
from aegis_pq.handshake import Initiator, Responder, run_handshake
from aegis_pq.channel import SecureChannel, ChannelConfig, HDR
from aegis_pq.pipeline import Sender, Receiver, body_size_for, record_size
from aegis_pq.errors import Reason


def setup(pki, clock, k, n, max_len=256):
    ca, creds = pki
    ik, rk = run_handshake(Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock),
                           Responder("rtu-07", creds["rtu-07"], ca.cert, clock))
    cfg = ChannelConfig(body_size=body_size_for(max_len, k))
    return Sender(SecureChannel(ik, clock, cfg), k, n), Receiver(SecureChannel(rk, clock, cfg))


@pytest.mark.parametrize("k,n", [(5, 5), (5, 7), (10, 13), (20, 20)])
def test_delivery_all_fragments(pki, clock, k, n):
    s, r = setup(pki, clock, k, n)
    m = b"AGC: unit G2 setpoint +2.50 MW"
    mid, recs = s.seal_message(m, 50)
    assert len({len(x) for x in recs}) == 1
    out = [r.receive(x) for x in recs]
    assert [o for o in out if o] == [(mid, m)]


def test_any_k_of_n_and_reordering(pki, clock):
    s, r = setup(pki, clock, 5, 8)
    m = os.urandom(120)
    mid, recs = s.seal_message(m, 50)
    keep = random.Random(5).sample(recs, 5)
    res = [r.receive(x) for x in keep]
    assert res[-1] == (mid, m) and all(x is None for x in res[:-1])


def test_k_minus_1_never_delivers(pki, clock):
    s, r = setup(pki, clock, 5, 8)
    mid, recs = s.seal_message(b"trip", 50)
    assert all(r.receive(x) is None for x in recs[:4])
    r.expire(mid)
    assert r.rejects.get(Reason.INCOMPLETE) == 1


def test_corrupted_fragment_is_erasure(pki, clock):
    s, r = setup(pki, clock, 5, 7)
    m = b"open 52-3"
    mid, recs = s.seal_message(m, 50)
    bad = bytearray(recs[0]); bad[HDR.size + 5] ^= 1
    assert r.receive(bytes(bad)) is None
    outs = [r.receive(x) for x in recs[1:]]
    assert (mid, m) in outs and r.rejects[Reason.AUTH_FAIL] == 1


def test_duplicates_and_replays_do_not_redeliver(pki, clock):
    s, r = setup(pki, clock, 3, 4)
    mid, recs = s.seal_message(b"x", 50)
    got = [r.receive(x) for x in recs]
    assert sum(1 for g in got if g) == 1
    assert all(r.receive(x) is None for x in recs)   # replays
    assert r.rejects[Reason.REPLAY] == 4


def test_late_fragments_rejected(pki, clock):
    s, r = setup(pki, clock, 5, 5)
    mid, recs = s.seal_message(b"late", 20)
    for x in recs[:3]:
        r.receive(x)
    clock.advance(25)
    assert all(r.receive(x) is None for x in recs[3:])
    assert r.rejects[Reason.DEADLINE] == 2


def test_dummies_same_size_and_ignored(pki, clock):
    s, r = setup(pki, clock, 5, 7)
    mid, recs = s.seal_message(b"cmd", 50)
    d = s.seal_dummy()
    assert len(d) == len(recs[0]) == record_size(s.chan.cfg.body_size)
    assert r.receive(d) is None and r.chan.stats["dummies_accepted"] == 1


def test_interleaved_messages(pki, clock):
    s, r = setup(pki, clock, 4, 6)
    a = s.seal_message(b"msg-A", 50); b = s.seal_message(b"msg-B", 50)
    mixed = [x for pair in zip(a[1], b[1]) for x in pair]
    got = [g for g in (r.receive(x) for x in mixed) if g]
    assert sorted(got) == sorted([(a[0], b"msg-A"), (b[0], b"msg-B")])


def test_inconsistent_fragment_metadata_rejected(pki, clock):
    """A sender bug/attack that labels shards of one msg_id with different (k,n)."""
    s, r = setup(pki, clock, 4, 6)
    mid, frags = s.fragment(b"zzz")
    from aegis_pq.pipeline import FRAG
    import struct
    f0 = frags[0]
    forged = FRAG.pack(mid, 1, 3, 6, struct.unpack_from(">I", f0, 7)[0]) + frags[1][FRAG.size:]
    r.receive(s.chan.seal(f0, 50)); r.receive(s.chan.seal(forged, 50))
    assert r.rejects[Reason.INTEGRITY] == 1
