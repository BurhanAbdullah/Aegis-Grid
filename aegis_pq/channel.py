"""AGP/1 record layer.

Record = header || AES-256-GCM(body)
  header (20 bytes, cleartext, used as AAD):
      0xA6 | version u8 | session_id 8B | epoch u16 | seq u64
  body plaintext:
      type u8 (1 = data, 2 = dummy) | t_gen_us u64 | deadline_us u32 |
      payload_len u16 | payload | zero padding to `body_size` (if fixed-size)

Nonce: 12-byte per-epoch IV XOR (0^4 || seq_be64)  (TLS 1.3 construction).
Keys:  key_e, iv_e = HKDF-Expand(secret_e, "key"/"iv"); secret_{e+1} =
       HKDF-Expand(secret_e, "key update").  Old secrets are erased after use.

Receiver order of checks (all failures raise Reject, nothing is returned):
  1. parse header; session id; epoch ∈ {current-1 (grace), current, current+1}
  2. replay window check (sliding window of W sequence numbers per epoch)
  3. AEAD open                                  -> AUTH_FAIL
  4. window update (only after authentication)
  5. session lifetime                           -> SESSION_EXPIRED
  6. deadline: now <= t_gen + deadline + skew   -> DEADLINE
Sender refuses to send after session lifetime / record limit (SESSION_EXPIRED)
and never reuses (epoch, seq).
"""
import struct
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.exceptions import InvalidTag

from .errors import Reject, Reason
from .suites import SUITES

REC_MAGIC = 0xA6
REC_VERSION = 1
HDR = struct.Struct(">BB8sHQ")       # 20 bytes
INNER = struct.Struct(">BQIH")       # 15 bytes
TAG_LEN = 16
TYPE_DATA, TYPE_DUMMY = 1, 2


@dataclass
class ChannelConfig:
    replay_window: int = 1024          # W, sequence numbers tracked per epoch
    rekey_every: int = 1 << 16         # records per epoch before key update
    max_lifetime_ms: float = 3_600_000.0   # session expiry (1 h)
    max_records: int = 1 << 32         # hard cap per session
    clock_skew_ms: float = 1.0         # ε_clk tolerance in deadline check (ASSUMPTION)
    body_size: int = 0                 # 0 = variable size; >0 = pad every record body


def _derive(suite, secret, label, n):
    return HKDFExpand(algorithm=suite.hash_alg(), length=n, info=b"AGP1 rec " + label).derive(secret)


class _EpochKeys:
    __slots__ = ("epoch", "secret", "aead", "iv")

    def __init__(self, suite, secret, epoch):
        self.epoch = epoch
        self.secret = secret
        self.aead = AESGCM(_derive(suite, secret, b"key", 32))
        self.iv = _derive(suite, secret, b"iv", 12)

    def nonce(self, seq):
        s = (0).to_bytes(4, "big") + seq.to_bytes(8, "big")
        return bytes(a ^ b for a, b in zip(self.iv, s))

    def next(self, suite):
        return _EpochKeys(suite, _derive(suite, self.secret, b"key update", len(self.secret)), self.epoch + 1)


class ReplayWindow:
    """RFC 4303-style sliding window over 64-bit sequence numbers."""

    def __init__(self, w):
        self.w, self.top, self.bits = w, -1, 0

    def check(self, seq):
        if seq > self.top:
            return
        if self.top - seq >= self.w:
            raise Reject(Reason.TOO_OLD)
        if (self.bits >> (self.top - seq)) & 1:
            raise Reject(Reason.REPLAY)

    def update(self, seq):
        if seq > self.top:
            shift = seq - self.top
            self.bits = ((self.bits << shift) | 1) & ((1 << self.w) - 1) if shift < self.w else 1
            self.top = seq
        else:
            self.bits |= 1 << (self.top - seq)


class SecureChannel:
    def __init__(self, keys, clock, cfg: ChannelConfig = None):
        self.suite = SUITES[keys.suite_code]
        self.sid = keys.session_id
        self.clock = clock
        self.cfg = cfg or ChannelConfig()
        self.t0 = keys.established_ms
        self._tx = _EpochKeys(self.suite, keys.send_secret, 0)
        self._tx_seq = 0
        self._tx_total = 0
        self._rx = {0: _EpochKeys(self.suite, keys.recv_secret, 0)}
        self._rx_cur = 0
        self._win = {0: ReplayWindow(self.cfg.replay_window)}
        self.nonces_used = None        # tests may set to a set() to audit nonce uniqueness
        self.stats = {"sent": 0, "accepted": 0, "dummies_accepted": 0, "rekeys_tx": 0, "rekeys_rx": 0}

    # ------------------------------------------------------------------ send
    def _expired(self):
        return (self.clock.now_ms() - self.t0) > self.cfg.max_lifetime_ms

    def seal(self, payload: bytes, deadline_ms: float, rtype: int = TYPE_DATA, t_gen_ms: float = None) -> bytes:
        if self._expired() or self._tx_total >= self.cfg.max_records:
            raise Reject(Reason.SESSION_EXPIRED, "sender")
        if self._tx_seq >= self.cfg.rekey_every:
            self._tx = self._tx.next(self.suite)
            self._tx_seq = 0
            self.stats["rekeys_tx"] += 1
        t_gen = self.clock.now_ms() if t_gen_ms is None else t_gen_ms
        body = INNER.pack(rtype, int(t_gen * 1000), int(deadline_ms * 1000), len(payload)) + payload
        if self.cfg.body_size:
            if len(body) > self.cfg.body_size:
                raise ValueError("payload exceeds fixed body size")
            body += b"\x00" * (self.cfg.body_size - len(body))
        hdr = HDR.pack(REC_MAGIC, REC_VERSION, self.sid, self._tx.epoch, self._tx_seq)
        nonce = self._tx.nonce(self._tx_seq)
        if self.nonces_used is not None:
            key_id = (self._tx.epoch, nonce)
            assert key_id not in self.nonces_used, "nonce reuse"
            self.nonces_used.add(key_id)
        ct = self._tx.aead.encrypt(nonce, body, hdr)
        self._tx_seq += 1
        self._tx_total += 1
        self.stats["sent"] += 1
        return hdr + ct

    # --------------------------------------------------------------- receive
    def _keys_for(self, epoch):
        if epoch in self._rx:
            return self._rx[epoch]
        if epoch == self._rx_cur + 1:
            return self._rx[self._rx_cur].next(self.suite)      # tentative; committed after auth
        raise Reject(Reason.WRONG_EPOCH)

    def open(self, record: bytes):
        """Return (rtype, payload, t_gen_ms, deadline_ms) or raise Reject."""
        if len(record) < HDR.size + INNER.size + TAG_LEN:
            raise Reject(Reason.MALFORMED, "short record")
        magic, ver, sid, epoch, seq = HDR.unpack_from(record)
        if magic != REC_MAGIC or ver != REC_VERSION:
            raise Reject(Reason.BAD_VERSION)
        if sid != self.sid:
            raise Reject(Reason.WRONG_SESSION)
        keys = self._keys_for(epoch)
        win = self._win.get(epoch) or ReplayWindow(self.cfg.replay_window)
        win.check(seq)
        try:
            body = keys.aead.decrypt(keys.nonce(seq), record[HDR.size:], record[:HDR.size])
        except InvalidTag:
            raise Reject(Reason.AUTH_FAIL)
        if epoch not in self._rx:                     # authenticated key update: commit
            self._rx[epoch] = keys
            self._win[epoch] = win
            # keep exactly one previous epoch for reordering grace; erase older
            for e in [e for e in self._rx if e < epoch - 1]:
                del self._rx[e]
                del self._win[e]
            self._rx_cur = epoch
            self.stats["rekeys_rx"] += 1
        win.update(seq)
        if self._expired():
            raise Reject(Reason.SESSION_EXPIRED, "receiver")
        rtype, t_gen_us, dl_us, plen = INNER.unpack_from(body)
        if INNER.size + plen > len(body) or rtype not in (TYPE_DATA, TYPE_DUMMY):
            raise Reject(Reason.MALFORMED, "inner length/type")
        t_gen, dl = t_gen_us / 1000.0, dl_us / 1000.0
        if self.clock.now_ms() > t_gen + dl + self.cfg.clock_skew_ms:
            raise Reject(Reason.DEADLINE)
        payload = body[INNER.size:INNER.size + plen]
        if rtype == TYPE_DUMMY:
            self.stats["dummies_accepted"] += 1
        else:
            self.stats["accepted"] += 1
        return rtype, payload, t_gen, dl
