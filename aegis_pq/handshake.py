"""AGP/1 handshake: mutually authenticated, ML-KEM key establishment.

Message flow (1 round trip + final flight; specification in
docs/protocol_specification.md §4):

  I -> R  ClientHello  = ver, client_random, offered suites, KEM key shares,
                         [X25519 share], initiator id, expected responder id
  R -> I  ServerHello  = ver, server_random, chosen suite, KEM ciphertext,
                         [X25519 share], responder cert,
                         ML-DSA sig_R over H("AGP1 server CV" || H(CH || SH_core)),
                         Finished_R = HMAC(fk_R, H(CH || SH_core || sig_R))
  I -> R  ClientFinish = initiator cert,
                         ML-DSA sig_I over H("AGP1 client CV" || H(CH || SH || CF_core)),
                         Finished_I = HMAC(fk_I, H(CH || SH || CF_core || sig_I))

Key schedule (HKDF, RFC 5869, hash = suite hash):
  ss   = ML-KEM shared secret [ || X25519 shared secret ]
  PRK  = HKDF-Extract(salt = client_random || server_random, IKM = ss)
  hs   = Expand(PRK, "hs"  || H(CH || SH_core))        -> fk_R, fk_I
  ms   = Expand(PRK, "ms"  || H(full transcript))      -> traffic secrets i2r, r2i, session id
The initiator's ephemeral ML-KEM private key is discarded after decapsulation,
giving forward secrecy against later compromise of long-term ML-DSA keys
(ANALYTICALLY DERIVED, conditional on ML-KEM IND-CCA2).
"""
import hmac
import os
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography import x509

from .errors import Reject, Reason
from .suites import SUITES, Policy, DEFAULT_POLICY
from .pki import Credential, validate_peer_cert
from .wire import Writer, Reader

VERSION = 1
MAGIC = b"AGP1"
T_CH, T_SH, T_CF = 1, 2, 3
_KEM_ID = {"ML-KEM-768": 1, "ML-KEM-1024": 2}
_KEM_NAME = {v: k for k, v in _KEM_ID.items()}


def _h(suite, *parts):
    d = hashes.Hash(suite.hash_alg())
    for p in parts:
        d.update(p)
    return d.finalize()


def _expand(suite, prk, label: bytes, ctx: bytes, n: int) -> bytes:
    return HKDFExpand(algorithm=suite.hash_alg(), length=n, info=b"AGP1 " + label + b"|" + ctx).derive(prk)


@dataclass
class SessionKeys:
    suite_code: int
    session_id: bytes
    i2r_secret: bytes
    r2i_secret: bytes
    transcript_hash: bytes
    peer_identity: str
    role: str                     # "initiator" | "responder"
    established_ms: float
    sizes: dict = field(default_factory=dict)   # bytes on the wire per flight

    @property
    def send_secret(self):
        return self.i2r_secret if self.role == "initiator" else self.r2i_secret

    @property
    def recv_secret(self):
        return self.r2i_secret if self.role == "initiator" else self.i2r_secret


def _cred_for(creds, suite):
    for c in creds:
        if c.sig_alg == suite.sig:
            return c
    raise Reject(Reason.NO_COMMON_SUITE, "no credential for suite signature algorithm")


class Initiator:
    def __init__(self, identity: str, peer_identity: str, creds: list, ca_cert: x509.Certificate,
                 clock, policy: Policy = DEFAULT_POLICY, share_kems=None):
        self.identity, self.peer, self.creds, self.ca, self.clock, self.policy = \
            identity, peer_identity, creds, ca_cert, clock, policy
        offered = [c for c in policy.preference if policy.acceptable(c)]
        if not offered:
            raise Reject(Reason.NO_COMMON_SUITE, "local policy empty")
        self.offered = tuple(offered)
        kems = share_kems or [SUITES[offered[0]].kem]
        self._kem_priv = {}
        self._x_priv = None
        self.state = "start"
        w = Writer().raw(MAGIC).u8(VERSION).u8(T_CH)
        self.client_random = os.urandom(32)
        w.raw(self.client_random).u8(len(offered))
        for c in offered:
            w.u16(c)
        w.u8(len(kems))
        for name in kems:
            s = next(SUITES[c] for c in offered if SUITES[c].kem == name)
            k = s.kem_generate()
            self._kem_priv[name] = k
            w.u8(_KEM_ID[name]).vec16(k.public_key().public_bytes_raw())
        if any(SUITES[c].hybrid_x25519 for c in offered):
            self._x_priv = x25519.X25519PrivateKey.generate()
            w.vec16(self._x_priv.public_key().public_bytes_raw())
        else:
            w.vec16(b"")
        w.vec16(identity.encode()).vec16(peer_identity.encode())
        self.ch = w.bytes()
        self.state = "sent_ch"

    def client_hello(self) -> bytes:
        return self.ch

    def process_server_hello(self, sh: bytes) -> bytes:
        if self.state != "sent_ch":
            raise Reject(Reason.STATE)
        self.state = "failed"           # any exception below leaves the object unusable
        r = Reader(sh)
        if r.raw(4) != MAGIC or r.u8() != VERSION or r.u8() != T_SH:
            raise Reject(Reason.BAD_VERSION)
        server_random = r.raw(32)
        code = r.u16()
        supported = tuple(r.u16() for _ in range(r.u8()))
        kem_ct = r.vec16()
        x_pub = r.vec16()
        cert_der = r.vec32()
        core_end2 = r.i
        sig = r.vec16()
        fin = r.raw(SUITES[code].hash_alg().digest_size if code in SUITES else 0)
        r.end()
        if code not in self.offered or not self.policy.acceptable(code):
            raise Reject(Reason.DOWNGRADE, "responder chose a suite not offered/acceptable")
        # Downgrade rule: the responder lists the suites it supports (signed below,
        # together with our own ClientHello).  The pick must equal our most-preferred
        # offered suite that the responder supports and for which we sent a share.
        suite = SUITES[code]
        if suite.kem not in self._kem_priv:
            raise Reject(Reason.DOWNGRADE, "suite KEM without a key share")
        expected = next((c for c in self.offered if c in supported and SUITES[c].kem in self._kem_priv), None)
        if code != expected:
            raise Reject(Reason.DOWNGRADE, "responder did not pick the preferred mutually supported suite")
        try:
            ss = self._kem_priv[suite.kem].decapsulate(kem_ct)
        except Exception:
            raise Reject(Reason.BAD_KEY, "ML-KEM decapsulation error")
        if suite.hybrid_x25519:
            try:
                ss += self._x_priv.exchange(x25519.X25519PublicKey.from_public_bytes(x_pub))
            except Exception:
                raise Reject(Reason.BAD_KEY, "bad X25519 share")
        elif x_pub:
            raise Reject(Reason.MALFORMED, "unexpected X25519 share")
        # discard ephemeral secrets (forward secrecy)
        self._kem_priv.clear()
        self._x_priv = None
        sh_core = sh[:core_end2]
        th1 = _h(suite, self.ch, sh_core)
        peer_pub = validate_peer_cert(cert_der, self.ca, self.peer, suite.sig, self.clock.now_ms())
        try:
            peer_pub.verify(sig, b"AGP1 server CV" + th1)
        except InvalidSignature:
            raise Reject(Reason.BAD_SIGNATURE, "responder signature")
        prk = _extract(suite, self.client_random + server_random, ss)
        hs = _expand(suite, prk, b"hs", th1, suite.hash_alg().digest_size)
        fk_r = _expand(suite, hs, b"finished R", b"", suite.hash_alg().digest_size)
        fk_i = _expand(suite, hs, b"finished I", b"", suite.hash_alg().digest_size)
        exp_fin = hmac.new(fk_r, _h(suite, self.ch, sh_core, sig), suite.hash.replace("-", "").lower()).digest()
        if not hmac.compare_digest(exp_fin, fin):
            raise Reject(Reason.BAD_FINISHED, "responder finished")
        cred = _cred_for(self.creds, suite)
        cf_core = Writer().raw(MAGIC).u8(VERSION).u8(T_CF).vec32(cred.cert_der).bytes()
        th2 = _h(suite, self.ch, sh, cf_core)
        sig_i = cred.key.sign(b"AGP1 client CV" + th2)
        fin_i = hmac.new(fk_i, _h(suite, self.ch, sh, cf_core, sig_i), suite.hash.replace("-", "").lower()).digest()
        cf = Writer().raw(cf_core).vec16(sig_i).raw(fin_i).bytes()
        th_full = _h(suite, self.ch, sh, cf)
        self.keys = _traffic(suite, prk, th_full, self.peer, "initiator", self.clock.now_ms(),
                             {"client_hello": len(self.ch), "server_hello": len(sh), "client_finish": len(cf)})
        self.state = "done"
        return cf


class Responder:
    def __init__(self, identity: str, creds: list, ca_cert: x509.Certificate, clock,
                 policy: Policy = DEFAULT_POLICY, allowed_peers=None):
        self.identity, self.creds, self.ca, self.clock, self.policy = identity, creds, ca_cert, clock, policy
        self.allowed_peers = allowed_peers
        self.state = "start"

    def process_client_hello(self, ch: bytes) -> bytes:
        if self.state != "start":
            raise Reject(Reason.STATE)
        self.state = "failed"
        r = Reader(ch)
        if r.raw(4) != MAGIC or r.u8() != VERSION or r.u8() != T_CH:
            raise Reject(Reason.BAD_VERSION)
        client_random = r.raw(32)
        offered = tuple(r.u16() for _ in range(r.u8()))
        shares = {}
        for _ in range(r.u8()):
            kid = r.u8()
            pk = r.vec16()
            if kid not in _KEM_NAME:
                raise Reject(Reason.MALFORMED, "unknown KEM id")
            shares[_KEM_NAME[kid]] = pk
        x_pub = r.vec16()
        peer_id = r.vec16().decode("utf-8", "strict")
        target = r.vec16().decode("utf-8", "strict")
        r.end()
        if target != self.identity:
            raise Reject(Reason.WRONG_PEER, "ClientHello addressed to another responder")
        if self.allowed_peers is not None and peer_id not in self.allowed_peers:
            raise Reject(Reason.WRONG_PEER, "initiator not authorised")
        # pick the initiator's most-preferred offered suite that we accept and
        # for which a key share was sent (initiator order; see downgrade rule)
        code = next((c for c in offered if c in SUITES and SUITES[c].kem in shares
                     and self.policy.acceptable(c)), None)
        if code is None:
            raise Reject(Reason.NO_COMMON_SUITE)
        suite = SUITES[code]
        try:
            pk = suite.kem_public_from_bytes(shares[suite.kem])
            ss, kem_ct = pk.encapsulate()
        except Exception:
            raise Reject(Reason.BAD_KEY, "invalid ML-KEM public key")
        x_out = b""
        if suite.hybrid_x25519:
            try:
                xp = x25519.X25519PrivateKey.generate()
                ss += xp.exchange(x25519.X25519PublicKey.from_public_bytes(x_pub))
                x_out = xp.public_key().public_bytes_raw()
            except Exception:
                raise Reject(Reason.BAD_KEY, "bad X25519 share")
        server_random = os.urandom(32)
        cred = _cred_for(self.creds, suite)
        sup = [c for c in self.policy.preference if self.policy.acceptable(c)]
        w = Writer().raw(MAGIC).u8(VERSION).u8(T_SH).raw(server_random).u16(code).u8(len(sup))
        for c in sup:
            w.u16(c)
        sh_core = (w.vec16(kem_ct).vec16(x_out).vec32(cred.cert_der).bytes())
        th1 = _h(suite, ch, sh_core)
        sig = cred.key.sign(b"AGP1 server CV" + th1)
        prk = _extract(suite, client_random + server_random, ss)
        hs = _expand(suite, prk, b"hs", th1, suite.hash_alg().digest_size)
        self._fk_r = _expand(suite, hs, b"finished R", b"", suite.hash_alg().digest_size)
        self._fk_i = _expand(suite, hs, b"finished I", b"", suite.hash_alg().digest_size)
        fin = hmac.new(self._fk_r, _h(suite, ch, sh_core, sig), suite.hash.replace("-", "").lower()).digest()
        sh = Writer().raw(sh_core).vec16(sig).raw(fin).bytes()
        self._ctx = (suite, prk, ch, sh, peer_id)
        self.state = "sent_sh"
        return sh

    def process_client_finish(self, cf: bytes) -> SessionKeys:
        if self.state != "sent_sh":
            raise Reject(Reason.STATE)
        self.state = "failed"
        suite, prk, ch, sh, peer_id = self._ctx
        r = Reader(cf)
        if r.raw(4) != MAGIC or r.u8() != VERSION or r.u8() != T_CF:
            raise Reject(Reason.BAD_VERSION)
        cert_der = r.vec32()
        core_end = r.i
        sig_i = r.vec16()
        fin_i = r.raw(suite.hash_alg().digest_size)
        r.end()
        cf_core = cf[:core_end]
        th2 = _h(suite, ch, sh, cf_core)
        peer_pub = validate_peer_cert(cert_der, self.ca, peer_id, suite.sig, self.clock.now_ms())
        try:
            peer_pub.verify(sig_i, b"AGP1 client CV" + th2)
        except InvalidSignature:
            raise Reject(Reason.BAD_SIGNATURE, "initiator signature")
        exp = hmac.new(self._fk_i, _h(suite, ch, sh, cf_core, sig_i), suite.hash.replace("-", "").lower()).digest()
        if not hmac.compare_digest(exp, fin_i):
            raise Reject(Reason.BAD_FINISHED, "initiator finished")
        th_full = _h(suite, ch, sh, cf)
        self.keys = _traffic(suite, prk, th_full, peer_id, "responder", self.clock.now_ms(),
                             {"client_hello": len(ch), "server_hello": len(sh), "client_finish": len(cf)})
        self._ctx = None
        self.state = "done"
        return self.keys


def _extract(suite, salt, ikm):
    h = hmac.new(salt, ikm, suite.hash.replace("-", "").lower())
    return h.digest()


def _traffic(suite, prk, th_full, peer, role, now_ms, sizes):
    n = suite.hash_alg().digest_size
    ms = _expand(suite, prk, b"ms", th_full, n)
    return SessionKeys(
        suite_code=suite.code,
        session_id=_expand(suite, ms, b"session id", b"", 8),
        i2r_secret=_expand(suite, ms, b"i2r traffic", b"", n),
        r2i_secret=_expand(suite, ms, b"r2i traffic", b"", n),
        transcript_hash=th_full, peer_identity=peer, role=role, established_ms=now_ms, sizes=sizes)


def run_handshake(initiator: Initiator, responder: Responder):
    """In-memory convenience: returns (initiator_keys, responder_keys)."""
    sh = responder.process_client_hello(initiator.client_hello())
    cf = initiator.process_server_hello(sh)
    rk = responder.process_client_finish(cf)
    return initiator.keys, rk
