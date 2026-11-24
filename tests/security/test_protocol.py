"""Security tests for the AGP/1 handshake and record layer (Milestone 2).

Each test asserts that an attack or malformed input is *rejected with the
expected reason* and that no plaintext is returned.
"""
import os
import pytest
from aegis_pq.errors import Reject, Reason
from aegis_pq.handshake import Initiator, Responder, run_handshake
from aegis_pq.channel import SecureChannel, ChannelConfig, TYPE_DUMMY, HDR
from aegis_pq.suites import Policy, SUITES
from aegis_pq.pki import GridCA


def mk(pki, clock, ipol=None, rpol=None, peer="rtu-07", share_kems=None):
    ca, creds = pki
    i = Initiator("cc-01", peer, creds["cc-01"], ca.cert, clock, **({"policy": ipol} if ipol else {}),
                  share_kems=share_kems)
    r = Responder(peer, creds[peer], ca.cert, clock, **({"policy": rpol} if rpol else {}))
    return i, r


def channels(pki, clock, cfg=None, **kw):
    i, r = mk(pki, clock, **kw)
    ik, rk = run_handshake(i, r)
    return SecureChannel(ik, clock, cfg), SecureChannel(rk, clock, cfg), ik, rk


def expect(reason, fn, *a):
    with pytest.raises(Reject) as e:
        fn(*a)
    assert e.value.reason == reason, e.value
    return e.value


# ---------------------------------------------------------------- handshake
@pytest.mark.parametrize("code", [0x0101, 0x0102, 0x0201, 0x0301])
def test_handshake_all_suites_agree_on_keys(pki, clock, code):
    pol = Policy(preference=(code,), min_category=SUITES[code].nist_category)
    i, r = mk(pki, clock, ipol=pol, rpol=pol)
    ik, rk = run_handshake(i, r)
    assert ik.session_id == rk.session_id and ik.i2r_secret == rk.i2r_secret and ik.r2i_secret == rk.r2i_secret
    assert ik.i2r_secret != ik.r2i_secret
    assert ik.suite_code == code


def test_end_to_end_message(pki, clock):
    a, b, *_ = channels(pki, clock)
    rec = a.seal(b"AGC raise 2.5 MW", deadline_ms=100)
    assert b.open(rec)[1] == b"AGC raise 2.5 MW"
    rec2 = b.seal(b"ack", deadline_ms=100)
    assert a.open(rec2)[1] == b"ack"


def test_tampered_server_hello_signature(pki, clock):
    i, r = mk(pki, clock)
    sh = bytearray(r.process_client_hello(i.client_hello()))
    sh[-60] ^= 1                                      # inside sig or finished
    with pytest.raises(Reject) as e:
        i.process_server_hello(bytes(sh))
    assert e.value.reason in (Reason.BAD_SIGNATURE, Reason.BAD_FINISHED)


def test_tampered_kem_ciphertext_fails(pki, clock):
    i, r = mk(pki, clock)
    sh = bytearray(r.process_client_hello(i.client_hello()))
    nsup = sh[4 + 2 + 32 + 2]
    sh[4 + 2 + 32 + 2 + 1 + 2 * nsup + 2 + 10] ^= 0xFF   # a byte inside kem_ct
    # ML-KEM implicit rejection yields a different secret -> signature still valid
    # over the *modified* transcript? No: signature covers kem_ct, so it fails.
    expect(Reason.BAD_SIGNATURE, i.process_server_hello, bytes(sh))


def test_invalid_kem_public_key(pki, clock):
    i, r = mk(pki, clock)
    ch = bytearray(i.client_hello())
    # replace the ML-KEM share with a wrong-length value
    off = 4 + 2 + 32 + 1 + 2 * len(i.offered) + 1 + 1
    ln = int.from_bytes(ch[off:off + 2], "big")
    bad = ch[:off] + (10).to_bytes(2, "big") + b"\x00" * 10 + ch[off + 2 + ln:]
    expect(Reason.BAD_KEY, r.process_client_hello, bytes(bad))


def test_wrong_ca_certificate_rejected(pki, clock):
    ca, creds = pki
    rogue = GridCA(now_ms=clock.now_ms())
    fake = [rogue.issue("rtu-07", "ML-DSA-65", now_ms=clock.now_ms())]
    i = Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock)
    r = Responder("rtu-07", fake, rogue.cert, clock)
    sh = r.process_client_hello(i.client_hello())
    expect(Reason.BAD_CERT, i.process_server_hello, sh)


def test_expired_certificate_rejected(pki, clock):
    ca, creds = pki
    short = [ca.issue("rtu-07", "ML-DSA-65", now_ms=clock.now_ms(), valid_s=10)]
    i = Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock)
    r = Responder("rtu-07", short, ca.cert, clock)
    clock.advance(120_000)
    sh = r.process_client_hello(i.client_hello())
    expect(Reason.CERT_EXPIRED, i.process_server_hello, sh)


def test_wrong_peer_identity_rejected(pki, clock):
    ca, creds = pki
    # rtu-08 answers a hello addressed to rtu-07 using its own valid certificate
    i = Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock)
    r = Responder("rtu-08", creds["rtu-08"], ca.cert, clock)
    expect(Reason.WRONG_PEER, r.process_client_hello, i.client_hello())
    # and a responder that ignores the target field is caught by certificate CN check
    r2 = Responder("rtu-07", creds["rtu-08"], ca.cert, clock)
    sh = r2.process_client_hello(i.client_hello())
    expect(Reason.WRONG_PEER, i.process_server_hello, sh)


def test_ca_cert_as_end_entity_rejected(pki, clock):
    ca, creds = pki
    bad = [ca.issue("rtu-07", "ML-DSA-65", now_ms=clock.now_ms(), ca_flag=True)]
    i = Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock)
    r = Responder("rtu-07", bad, ca.cert, clock)
    expect(Reason.BAD_CERT, i.process_server_hello, r.process_client_hello(i.client_hello()))


def test_invalid_client_signature_rejected(pki, clock):
    i, r = mk(pki, clock)
    sh = r.process_client_hello(i.client_hello())
    cf = bytearray(i.process_server_hello(sh))
    cf[-100] ^= 1
    with pytest.raises(Reject) as e:
        r.process_client_finish(bytes(cf))
    assert e.value.reason in (Reason.BAD_SIGNATURE, Reason.BAD_FINISHED, Reason.MALFORMED)


def test_downgrade_stripping_rejected(pki, clock):
    """MITM removes the preferred suite from ClientHello; responder picks a weaker one."""
    ca, creds = pki
    pol = Policy(preference=(0x0201, 0x0101), min_category=3)
    i = Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock, policy=pol,
                  share_kems=["ML-KEM-1024", "ML-KEM-768"])
    ch = bytearray(i.client_hello())
    # offered list sits at offset 4+2+32: count u8 then u16 codes; drop 0x0201
    off = 4 + 2 + 32
    assert ch[off] == 2 and ch[off + 1:off + 3] == b"\x02\x01"
    stripped = ch[:off] + b"\x01" + ch[off + 3:]
    r = Responder("rtu-07", creds["rtu-07"], ca.cert, clock, policy=pol)
    sh = r.process_client_hello(bytes(stripped))
    with pytest.raises(Reject) as e:
        i.process_server_hello(sh)
    assert e.value.reason in (Reason.DOWNGRADE, Reason.BAD_SIGNATURE)


def test_legit_fallback_when_responder_lacks_preferred_suite(pki, clock):
    ca, creds = pki
    ipol = Policy(preference=(0x0201, 0x0101), min_category=3)
    i = Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock, policy=ipol,
                  share_kems=["ML-KEM-1024", "ML-KEM-768"])
    r = Responder("rtu-07", creds["rtu-07"], ca.cert, clock, policy=Policy(preference=(0x0101,), min_category=3))
    ik, rk = run_handshake(i, r)
    assert ik.suite_code == rk.suite_code == 0x0101


def test_responder_choosing_non_preferred_suite_is_downgrade(pki, clock, monkeypatch):
    """A (malicious or buggy) responder that supports the preferred suite but picks another."""
    ca, creds = pki
    pol = Policy(preference=(0x0201, 0x0101), min_category=3)
    i = Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock, policy=pol,
                  share_kems=["ML-KEM-1024", "ML-KEM-768"])
    r = Responder("rtu-07", creds["rtu-07"], ca.cert, clock, policy=pol)
    ch = bytearray(i.client_hello())
    # make the responder see 0x0101 first, so it picks it, while its signed
    # 'supported' list still advertises 0x0201
    off = 4 + 2 + 32
    swapped = ch[:off + 1] + b"\x01\x01\x02\x01" + ch[off + 5:]
    sh = r.process_client_hello(bytes(swapped))
    with pytest.raises(Reject) as e:
        i.process_server_hello(sh)
    assert e.value.reason in (Reason.DOWNGRADE, Reason.BAD_SIGNATURE)


def test_below_floor_suite_never_negotiated(pki, clock):
    ipol = Policy(preference=(0x0101,), min_category=3)
    rpol = Policy(preference=(0x0301,), min_category=2)
    i, r = mk(pki, clock, ipol=ipol, rpol=rpol)
    expect(Reason.NO_COMMON_SUITE, r.process_client_hello, i.client_hello())


def test_handshake_state_machine(pki, clock):
    i, r = mk(pki, clock)
    expect(Reason.STATE, r.process_client_finish, b"x")
    sh = r.process_client_hello(i.client_hello())
    expect(Reason.STATE, r.process_client_hello, i.client_hello())
    i.process_server_hello(sh)
    expect(Reason.STATE, i.process_server_hello, sh)


@pytest.mark.parametrize("cut", [0, 5, 37, 200])
def test_truncated_handshake_messages(pki, clock, cut):
    i, r = mk(pki, clock)
    ch = i.client_hello()
    with pytest.raises(Reject) as e:
        r.process_client_hello(ch[:cut])
    assert e.value.reason in (Reason.MALFORMED, Reason.BAD_VERSION)


def test_trailing_bytes_rejected(pki, clock):
    i, r = mk(pki, clock)
    expect(Reason.MALFORMED, r.process_client_hello, i.client_hello() + b"\x00")


# ------------------------------------------------------------- record layer
def test_tampered_ciphertext_and_tag(pki, clock):
    a, b, *_ = channels(pki, clock)
    rec = bytearray(a.seal(b"open breaker 52-3", 100))
    for pos in (HDR.size + 3, len(rec) - 1):          # body byte, tag byte
        t = bytearray(rec); t[pos] ^= 1
        expect(Reason.AUTH_FAIL, b.open, bytes(t))
    assert b.open(bytes(rec))[1] == b"open breaker 52-3"   # original still valid


def test_tampered_header_is_authenticated(pki, clock):
    a, b, *_ = channels(pki, clock)
    rec = bytearray(a.seal(b"x", 100))
    rec[HDR.size - 1] ^= 1                              # change seq
    expect(Reason.AUTH_FAIL, b.open, bytes(rec))


def test_replay_rejected(pki, clock):
    a, b, *_ = channels(pki, clock)
    rec = a.seal(b"cmd", 100)
    b.open(rec)
    expect(Reason.REPLAY, b.open, rec)


def test_reordering_within_window_accepted_outside_rejected(pki, clock):
    a, b, *_ = channels(pki, clock, cfg=ChannelConfig(replay_window=8))
    recs = [a.seal(bytes([k]), 100) for k in range(20)]
    b.open(recs[10]); b.open(recs[5])                  # 5 is within 8 of 10
    expect(Reason.REPLAY, b.open, recs[5])
    b.open(recs[19])
    expect(Reason.TOO_OLD, b.open, recs[6])            # 19-6 >= 8


def test_late_message_rejected_by_deadline(pki, clock):
    a, b, *_ = channels(pki, clock, cfg=ChannelConfig(clock_skew_ms=1.0))
    rec = a.seal(b"setpoint", deadline_ms=20)
    clock.advance(21.5)
    expect(Reason.DEADLINE, b.open, rec)
    # and the late record cannot be replayed later
    expect(Reason.REPLAY, b.open, rec)


def test_on_time_message_accepted_at_boundary(pki, clock):
    a, b, *_ = channels(pki, clock, cfg=ChannelConfig(clock_skew_ms=1.0))
    rec = a.seal(b"setpoint", deadline_ms=20)
    clock.advance(20.9)
    assert b.open(rec)[1] == b"setpoint"


def test_session_expiry(pki, clock):
    cfg = ChannelConfig(max_lifetime_ms=1000)
    a, b, *_ = channels(pki, clock, cfg=cfg)
    rec = a.seal(b"x", 5000)
    clock.advance(1500)
    expect(Reason.SESSION_EXPIRED, b.open, rec)
    expect(Reason.SESSION_EXPIRED, a.seal, b"y", 10)


def test_key_rotation_and_nonce_uniqueness(pki, clock):
    cfg = ChannelConfig(rekey_every=50)
    a, b, *_ = channels(pki, clock, cfg=cfg)
    a.nonces_used = set()
    for k in range(520):
        assert b.open(a.seal(k.to_bytes(4, "big"), 100))[1] == k.to_bytes(4, "big")
    assert a.stats["rekeys_tx"] == 10 and b.stats["rekeys_rx"] == 10
    assert len(a.nonces_used) == 520


def test_old_epoch_erased_after_rotation(pki, clock):
    cfg = ChannelConfig(rekey_every=10)
    a, b, *_ = channels(pki, clock, cfg=cfg)
    old = [a.seal(b"e0", 100) for _ in range(10)]
    e1 = [a.seal(b"e1", 100) for _ in range(10)]
    e2 = [a.seal(b"e2", 100) for _ in range(10)]
    b.open(e1[0]); b.open(e2[0])
    expect(Reason.WRONG_EPOCH, b.open, old[3])          # epoch 0 keys erased
    assert b.open(e1[4])[1] == b"e1"                    # previous epoch kept for reordering


def test_epoch_skip_rejected(pki, clock):
    a, b, *_ = channels(pki, clock, cfg=ChannelConfig(rekey_every=5))
    recs = [a.seal(b"z", 100) for _ in range(12)]       # epochs 0,1,2
    expect(Reason.WRONG_EPOCH, b.open, recs[11])        # epoch 2 while receiver at 0


def test_session_separation(pki, clock):
    a1, b1, *_ = channels(pki, clock)
    a2, b2, *_ = channels(pki, clock)
    rec = a1.seal(b"for session 1", 100)
    expect(Reason.WRONG_SESSION, b2.open, rec)
    # forge session id to match: AEAD key differs -> AUTH_FAIL
    forged = rec[:2] + b2.sid + rec[10:]
    expect(Reason.AUTH_FAIL, b2.open, forged)


def test_concurrent_sessions_independent(pki, clock):
    pairs = [channels(pki, clock) for _ in range(5)]
    for k, (a, b, *_ ) in enumerate(pairs):
        assert b.open(a.seal(f"s{k}".encode(), 100))[1] == f"s{k}".encode()
    sids = {p[0].sid for p in pairs}
    assert len(sids) == 5


def test_reflection_rejected(pki, clock):
    a, b, *_ = channels(pki, clock)
    rec = a.seal(b"x", 100)
    expect(Reason.AUTH_FAIL, a.open, rec)               # own record reflected back


@pytest.mark.parametrize("n", [0, 1, 19, 20, 34, 50])
def test_truncated_records(pki, clock, n):
    a, b, *_ = channels(pki, clock)
    rec = a.seal(b"payload", 100)
    with pytest.raises(Reject) as e:
        b.open(rec[:n])
    assert e.value.reason in (Reason.MALFORMED, Reason.AUTH_FAIL)


def test_random_garbage_never_accepted(pki, clock):
    a, b, *_ = channels(pki, clock)
    for _ in range(500):
        junk = os.urandom(os.urandom(1)[0] + 1)
        with pytest.raises(Reject):
            b.open(junk)
    # garbage with correct header prefix
    good = a.seal(b"x", 100)
    for _ in range(200):
        with pytest.raises(Reject):
            b.open(good[:HDR.size] + os.urandom(len(good) - HDR.size))


def test_fixed_size_records_and_dummies(pki, clock):
    a, b, *_ = channels(pki, clock, cfg=ChannelConfig(body_size=256))
    r1 = a.seal(b"short", 100)
    r2 = a.seal(os.urandom(200), 100)
    r3 = a.seal(os.urandom(64), 100, rtype=TYPE_DUMMY)
    assert len(r1) == len(r2) == len(r3) == 20 + 256 + 16
    assert b.open(r3)[0] == TYPE_DUMMY and b.stats["dummies_accepted"] == 1


def test_reject_carries_no_plaintext(pki, clock):
    a, b, *_ = channels(pki, clock)
    secret = b"TRIP-ALL-FEEDERS"
    rec = bytearray(a.seal(secret, 100)); rec[-1] ^= 1
    try:
        b.open(bytes(rec))
    except Reject as e:
        assert secret not in str(e).encode() and not hasattr(e, "payload")


def test_forward_secrecy_ephemeral_keys_discarded(pki, clock):
    i, r = mk(pki, clock)
    run_handshake(i, r)
    assert i._kem_priv == {} and i._x_priv is None and r._ctx is None
