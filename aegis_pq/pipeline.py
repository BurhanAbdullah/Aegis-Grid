"""Bounded AGP/1 message pipeline: AONT -> RS(k,n) -> authenticated records.

The receiver is deliberately fail-closed under resource pressure. All limits are
per receiver/session and must be selected for the deployment workload.
"""
import math
import struct
from dataclasses import dataclass, field

from . import aont, erasure
from .channel import SecureChannel, TYPE_DATA, TYPE_DUMMY, INNER, HDR, TAG_LEN
from .errors import Reject, Reason

FRAG = struct.Struct(">IBBBI")  # msg_id u32 | index u8 | k u8 | n u8 | AONT length u32
MAX_WIRE_FRAGMENTS = 255


def body_size_for(max_msg_len: int, k: int) -> int:
    """Smallest fixed record-body size that fits one shard of a max-length message."""
    if not isinstance(max_msg_len, int) or max_msg_len < 0:
        raise ValueError("max_msg_len must be a non-negative integer")
    if not isinstance(k, int) or not 1 <= k <= MAX_WIRE_FRAGMENTS:
        raise ValueError("k must be in [1, 255]")
    y = max_msg_len + aont.OVERHEAD
    shard = -(-y // k)
    if FRAG.size + shard > 0xFFFF:
        raise ValueError("one fragment exceeds the AGP/1 u16 payload-length field")
    return INNER.size + FRAG.size + shard


def record_size(body_size: int) -> int:
    return HDR.size + body_size + TAG_LEN


@dataclass
class Sender:
    chan: SecureChannel
    k: int
    n: int
    next_id: int = 0
    max_message_bytes: int = 60 * 1024

    def __post_init__(self):
        if not (1 <= self.k <= self.n <= MAX_WIRE_FRAGMENTS):
            raise ValueError("require 1 <= k <= n <= 255")
        if self.max_message_bytes < 0:
            raise ValueError("max_message_bytes must be non-negative")
        if not 0 <= self.next_id <= 0xFFFFFFFF:
            raise ValueError("next_id must fit u32")

    def fragment(self, message: bytes):
        """Return (msg_id, list of n fragment payloads). Message IDs never wrap."""
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if len(message) > self.max_message_bytes:
            raise Reject(Reason.RESOURCE_LIMIT, "message exceeds sender limit")
        if self.next_id > 0xFFFFFFFF:
            raise Reject(Reason.RESOURCE_LIMIT, "message ID space exhausted; establish a new session")
        y = aont.transform(message)
        shards = erasure.encode(y, self.k, self.n)
        if any(FRAG.size + len(shard) > 0xFFFF for shard in shards):
            raise Reject(Reason.RESOURCE_LIMIT, "fragment exceeds AGP/1 u16 payload-length field")
        mid = self.next_id
        self.next_id += 1
        return mid, [FRAG.pack(mid, i, self.k, self.n, len(y)) + s for i, s in enumerate(shards)]

    def seal_message(self, message: bytes, deadline_ms: float, t_gen_ms: float = None):
        """Seal all fragments with one authenticated generation time and deadline."""
        if (not math.isfinite(float(deadline_ms)) or float(deadline_ms) < 0
                or float(deadline_ms) * 1000 > 0xFFFFFFFF):
            raise ValueError("deadline_ms must fit the authenticated u32 microsecond field")
        mid, frags = self.fragment(message)
        generated = self.chan.clock.now_ms() if t_gen_ms is None else float(t_gen_ms)
        if (not math.isfinite(generated) or generated < 0
                or generated * 1000 > 0xFFFFFFFFFFFFFFFF):
            raise ValueError("t_gen_ms must fit the authenticated u64 microsecond field")
        return mid, [self.chan.seal(f, deadline_ms, TYPE_DATA, generated) for f in frags]

    def seal_dummy(self, deadline_ms: float = 1e3):
        size = self.chan.cfg.body_size - INNER.size if self.chan.cfg.body_size else 0
        import os
        return self.chan.seal(os.urandom(size), deadline_ms, TYPE_DUMMY)


@dataclass
class Receiver:
    chan: SecureChannel
    # Preserve the original positional constructor fields for v6.0 callers.
    pending: dict = field(default_factory=dict)
    delivered: set = field(default_factory=set)
    rejects: dict = field(default_factory=dict)
    pending_bytes: int = 0
    max_pending_messages: int = 1024
    max_pending_bytes: int = 64 * 1024 * 1024
    max_message_bytes: int = 60 * 1024
    max_fragments: int = 255
    max_message_buffer_bytes: int = 1024 * 1024
    max_delivered_ids: int = 65536

    def __post_init__(self):
        limits = (self.max_pending_messages, self.max_pending_bytes,
                  self.max_message_bytes, self.max_fragments,
                  self.max_message_buffer_bytes, self.max_delivered_ids)
        if any(not isinstance(v, int) or v <= 0 for v in limits):
            raise ValueError("receiver resource limits must be positive integers")
        if self.max_fragments > MAX_WIRE_FRAGMENTS:
            raise ValueError("max_fragments cannot exceed 255 (wire field is u8)")

    def _count(self, reason):
        self.rejects[reason] = self.rejects.get(reason, 0) + 1

    def _drop_pending(self, msg_id):
        state = self.pending.pop(msg_id, None)
        if state is not None:
            self.pending_bytes -= state["bytes"]
        return state

    def expire_due(self, now_ms: float = None) -> int:
        """Expire incomplete messages. Call periodically even when no records arrive."""
        now = self.chan.clock.now_ms() if now_ms is None else float(now_ms)
        expired = [mid for mid, st in self.pending.items() if now > st["expires_at_ms"]]
        for mid in expired:
            self._drop_pending(mid)
            self._count(Reason.INCOMPLETE)
        return len(expired)

    def receive(self, record: bytes):
        """Process one record; return (msg_id, message) only on valid completion.

        Resource exhaustion, malformed metadata, expiry and reconstruction errors
        fail closed. The caller should schedule expire_due() independently.
        """
        self.expire_due()
        try:
            rtype, payload, t_gen, dl = self.chan.open(record)
        except Reject as e:
            self._count(e.reason)
            return None
        if rtype == TYPE_DUMMY:
            return None
        if len(payload) < FRAG.size:
            self._count(Reason.MALFORMED)
            return None

        mid, idx, k, n, ylen = FRAG.unpack_from(payload)
        shard = payload[FRAG.size:]
        if mid in self.delivered:
            return None
        if not (1 <= k <= n <= self.max_fragments) or idx >= n:
            self._count(Reason.MALFORMED)
            return None
        if ylen < aont.OVERHEAD or ylen > self.max_message_bytes + aont.OVERHEAD:
            self._count(Reason.RESOURCE_LIMIT)
            return None
        expected_shard_size = max(1, -(-ylen // k))
        if FRAG.size + expected_shard_size > 0xFFFF:
            self._count(Reason.RESOURCE_LIMIT)
            return None
        if len(shard) != expected_shard_size:
            self._count(Reason.MALFORMED)
            return None
        if expected_shard_size * n > self.max_message_buffer_bytes:
            self._count(Reason.RESOURCE_LIMIT)
            return None

        state = self.pending.get(mid)
        if state is None:
            if len(self.pending) >= self.max_pending_messages:
                self._count(Reason.RESOURCE_LIMIT)
                return None
            if len(self.delivered) >= self.max_delivered_ids:
                self._count(Reason.RESOURCE_LIMIT)
                return None
            state = {
                "k": k, "n": n, "len": ylen, "shards": {},
                "t_gen": t_gen, "deadline": dl,
                "expires_at_ms": t_gen + dl + self.chan.cfg.clock_skew_ms,
                "bytes": 0,
            }
            self.pending[mid] = state
        elif (state["k"], state["n"], state["len"]) != (k, n, ylen):
            self._drop_pending(mid)
            self._count(Reason.INTEGRITY)
            return None
        elif (state["t_gen"], state["deadline"]) != (t_gen, dl):
            self._drop_pending(mid)
            self._count(Reason.INTEGRITY)
            return None

        previous = state["shards"].get(idx)
        if previous is not None:
            if previous != shard:
                self._drop_pending(mid)
                self._count(Reason.INTEGRITY)
            return None
        if self.pending_bytes + len(shard) > self.max_pending_bytes:
            if not state["shards"]:
                self._drop_pending(mid)
            self._count(Reason.RESOURCE_LIMIT)
            return None

        state["shards"][idx] = shard
        state["bytes"] += len(shard)
        self.pending_bytes += len(shard)
        if len(state["shards"]) < k:
            return None

        try:
            y = erasure.decode(state["shards"], k, n, ylen)
            message = aont.inverse(y)
        except Reject as e:
            self._drop_pending(mid)
            self._count(e.reason)
            return None
        except (ValueError, struct.error, ZeroDivisionError):
            self._drop_pending(mid)
            self._count(Reason.MALFORMED)
            return None

        if len(self.delivered) >= self.max_delivered_ids:
            self._drop_pending(mid)
            self._count(Reason.RESOURCE_LIMIT)
            return None
        self._drop_pending(mid)
        self.delivered.add(mid)
        return mid, message

    def expire(self, msg_id):
        """Explicitly expire one incomplete message; M-hat = bottom."""
        if self._drop_pending(msg_id) is not None:
            self._count(Reason.INCOMPLETE)
