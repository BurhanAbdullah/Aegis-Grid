"""IEC 62351-6-style authentication-only baseline (simplified, not a conformant
implementation): each message carries a 64-bit sequence number, a timestamp and
an HMAC-SHA256 tag (truncated to 16 bytes here for size parity with AES-GCM)
under a pre-shared group key (in IEC 62351-9 distributed by GDOI, which is
outside this model). Provides integrity, origin authentication within the
group and replay detection; provides no confidentiality and no key
establishment (so no post-quantum key exchange).
"""
import hashlib, hmac, struct

HDR = struct.Struct(">QQ")       # seq, t_gen_us
TAG = 16


class HmacSender:
    def __init__(self, key):
        self.key, self.seq = key, 0

    def seal(self, msg, t_us):
        h = HDR.pack(self.seq, int(t_us)) + msg
        self.seq += 1
        return h + hmac.new(self.key, h, hashlib.sha256).digest()[:TAG]


class HmacReceiver:
    def __init__(self, key, max_age_us):
        self.key, self.last, self.max_age = key, -1, max_age_us

    def open(self, rec, now_us):
        h, tag = rec[:-TAG], rec[-TAG:]
        if not hmac.compare_digest(tag, hmac.new(self.key, h, hashlib.sha256).digest()[:TAG]):
            return None
        seq, t = HDR.unpack_from(h)
        if seq <= self.last or now_us - t > self.max_age:
            return None
        self.last = seq
        return h[HDR.size:]
