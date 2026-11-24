"""Deterministic length-prefixed binary encoding used by the handshake.

Only three field kinds exist: fixed bytes, u8/u16/u32 integers, and
length-prefixed byte strings (u16 or u32 length).  Any trailing or missing
bytes raise Reject(MALFORMED).
"""
import struct
from .errors import Reject, Reason


class Writer:
    def __init__(self):
        self.parts = []

    def u8(self, v): self.parts.append(struct.pack(">B", v)); return self
    def u16(self, v): self.parts.append(struct.pack(">H", v)); return self
    def u32(self, v): self.parts.append(struct.pack(">I", v)); return self
    def u64(self, v): self.parts.append(struct.pack(">Q", v)); return self
    def raw(self, b): self.parts.append(bytes(b)); return self

    def vec16(self, b):
        if len(b) > 0xFFFF:
            raise ValueError("field too long")
        return self.u16(len(b)).raw(b)

    def vec32(self, b): return self.u32(len(b)).raw(b)
    def bytes(self): return b"".join(self.parts)


class Reader:
    def __init__(self, data: bytes):
        self.d = memoryview(bytes(data))
        self.i = 0

    def _take(self, n):
        if n < 0 or self.i + n > len(self.d):
            raise Reject(Reason.MALFORMED, "truncated")
        out = bytes(self.d[self.i:self.i + n])
        self.i += n
        return out

    def u8(self): return struct.unpack(">B", self._take(1))[0]
    def u16(self): return struct.unpack(">H", self._take(2))[0]
    def u32(self): return struct.unpack(">I", self._take(4))[0]
    def u64(self): return struct.unpack(">Q", self._take(8))[0]
    def raw(self, n): return self._take(n)
    def vec16(self): return self._take(self.u16())
    def vec32(self): return self._take(self.u32())

    def end(self):
        if self.i != len(self.d):
            raise Reject(Reason.MALFORMED, "trailing bytes")
