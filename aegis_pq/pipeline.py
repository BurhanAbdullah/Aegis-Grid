"""Message pipeline: M -> AONT -> RS(k,n) -> n fixed-size AGP/1 records.

Fragment payload (inside the encrypted record body):
    msg_id u32 | idx u8 | k u8 | n u8 | aont_len u32 | shard bytes
The receiver collects shards per msg_id; after k distinct, consistent shards
it decodes, inverts the AONT and delivers M exactly once. Fewer than k shards
before the record deadlines expire => the message is never delivered (⊥).

The previous XOR transform (core/fragmentation.py) is retained only for the
audit comparison in EXP-004; it is not used here.
"""
import struct
from dataclasses import dataclass, field

from . import aont, erasure
from .channel import SecureChannel, TYPE_DATA, TYPE_DUMMY, INNER, HDR, TAG_LEN
from .errors import Reject, Reason

FRAG = struct.Struct(">IBBBI")    # 11 bytes


def body_size_for(max_msg_len: int, k: int) -> int:
    """Smallest fixed record-body size that fits one shard of a max-length message."""
    y = max_msg_len + aont.OVERHEAD
    shard = -(-y // k)
    return INNER.size + FRAG.size + shard


def record_size(body_size: int) -> int:
    return HDR.size + body_size + TAG_LEN


@dataclass
class Sender:
    chan: SecureChannel
    k: int
    n: int
    next_id: int = 0

    def fragment(self, message: bytes):
        """Return (msg_id, list of n fragment payloads)."""
        y = aont.transform(message)
        shards = erasure.encode(y, self.k, self.n)
        mid = self.next_id
        self.next_id = (self.next_id + 1) & 0xFFFFFFFF
        return mid, [FRAG.pack(mid, i, self.k, self.n, len(y)) + s for i, s in enumerate(shards)]

    def seal_message(self, message: bytes, deadline_ms: float, t_gen_ms: float = None):
        mid, frags = self.fragment(message)
        return mid, [self.chan.seal(f, deadline_ms, TYPE_DATA, t_gen_ms) for f in frags]

    def seal_dummy(self, deadline_ms: float = 1e3):
        size = self.chan.cfg.body_size - INNER.size if self.chan.cfg.body_size else 0
        import os
        return self.chan.seal(os.urandom(size), deadline_ms, TYPE_DUMMY)


@dataclass
class Receiver:
    chan: SecureChannel
    pending: dict = field(default_factory=dict)      # msg_id -> {"k","n","len","shards":{}}
    delivered: set = field(default_factory=set)
    rejects: dict = field(default_factory=dict)      # Reason -> count

    def _count(self, reason):
        self.rejects[reason] = self.rejects.get(reason, 0) + 1

    def receive(self, record: bytes):
        """Process one record. Returns (msg_id, message) when a message completes, else None.
        Never raises on adversarial input; rejections are counted."""
        try:
            rtype, payload, t_gen, dl = self.chan.open(record)
        except Reject as e:
            self._count(e.reason)
            return None
        if rtype == TYPE_DUMMY:
            return None
        if len(payload) < FRAG.size:
            self._count(Reason.MALFORMED); return None
        mid, idx, k, n, ylen = FRAG.unpack_from(payload)
        shard = payload[FRAG.size:]
        if mid in self.delivered:
            return None
        if not (1 <= k <= n) or idx >= n:
            self._count(Reason.MALFORMED); return None
        st = self.pending.setdefault(mid, {"k": k, "n": n, "len": ylen, "shards": {}})
        if (st["k"], st["n"], st["len"]) != (k, n, ylen):
            self._count(Reason.INTEGRITY); self.pending.pop(mid, None); return None
        st["shards"].setdefault(idx, shard)
        if len(st["shards"]) < k:
            return None
        try:
            y = erasure.decode(st["shards"], k, n, ylen)
            m = aont.inverse(y)
        except Reject as e:
            self._count(e.reason); self.pending.pop(mid, None); return None
        self.pending.pop(mid, None)
        self.delivered.add(mid)
        return mid, m

    def expire(self, msg_id):
        """Called by the application when a message's deadline passes: M̂ = ⊥."""
        if self.pending.pop(msg_id, None) is not None:
            self._count(Reason.INCOMPLETE)
