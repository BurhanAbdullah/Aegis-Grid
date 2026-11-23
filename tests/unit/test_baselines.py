import os, ssl
from baselines.iec62351_hmac import HmacSender, HmacReceiver
from baselines import tls13


def test_hmac_baseline_auth_replay_age():
    k = os.urandom(32)
    s, r = HmacSender(k), HmacReceiver(k, 1000)
    a = s.seal(b"trip", 10)
    assert r.open(a, 20) == b"trip"
    assert r.open(a, 21) is None                       # replay
    b = s.seal(b"x", 30)
    assert r.open(b[:-1] + bytes([b[-1] ^ 1]), 31) is None
    assert r.open(s.seal(b"y", 0), 5000) is None       # too old


def test_tls13_pq_group_and_mldsa_cert_verified(tmp_path):
    ca, crt, key = tls13.make_pki(str(tmp_path), "mldsa65")
    sctx, cctx = tls13.contexts(ca, crt, key)
    cb, sb, grp, cipher = tls13.memory_handshake(sctx, cctx)
    assert ssl.OPENSSL_VERSION.startswith("OpenSSL 3.5")
    assert tls13.GROUP_IDS.get(grp) == "X25519MLKEM768"   # default group of OpenSSL 3.5, verified on the wire
    assert sb > 5000                                       # ML-DSA-65 certificate chain + signature


def test_tls13_mutual_auth_requires_client_cert(tmp_path):
    ca, crt, key = tls13.make_pki(str(tmp_path), "mldsa65")
    sctx, cctx = tls13.contexts(ca, crt, key, mutual=True)
    cb, sb, grp, _ = tls13.memory_handshake(sctx, cctx)
    assert cb > 5000                                       # client now sends an ML-DSA-65 certificate + signature
    sctx2, _ = tls13.contexts(ca, crt, key, mutual=True)
    _, cnoc = tls13.contexts(ca, crt, key, mutual=False)
    import pytest
    with pytest.raises(Exception):
        tls13.memory_handshake(sctx2, cnoc)


def _chains(sctx, cctx):
    """Run an in-memory handshake and return the certificate chain lengths each side received."""
    ci, co, si, so = (ssl.MemoryBIO() for _ in range(4))
    c = cctx.wrap_bio(ci, co, server_hostname="rtu-07"); s = sctx.wrap_bio(si, so, server_side=True)
    for _ in range(10):
        for o, src, dst in ((c, co, si), (s, so, ci)):
            try:
                o.do_handshake()
            except ssl.SSLWantReadError:
                pass
            dst.write(src.read())
    return len(c.get_unverified_chain()), len(s.get_unverified_chain())


def test_tls13_mutual_autochain_sends_ca_and_leaf_only_does_not(tmp_path):
    ca, crt, key = tls13.make_pki(str(tmp_path), "mldsa65")
    assert _chains(*tls13.contexts(ca, crt, key, mutual=True)) == (2, 2)        # OpenSSL auto-chaining adds the CA
    assert _chains(*tls13.contexts(ca, crt, key, mutual=True, leaf_only=True)) == (1, 1)
