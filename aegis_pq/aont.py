"""All-or-nothing transform (AONT): CTR-mode package transform with an
OAEP-style key block.

Construction (byte strings; ‖ = concatenation):

    input   M  (0 ≤ |M| < 2^32)
    K       ← 32 uniformly random bytes (os.urandom)
    X       = len(M) as u32 ‖ M ‖ 0^16              (16-byte canary for integrity)
    C       = X ⊕ AES-256-CTR_K(IV = 0^16)            (|C| = |X|)
    T       = K ⊕ SHA-256(C)                         (32 bytes)
    output  Y = C ‖ T

Inverse: K = T ⊕ SHA-256(C);  X = C ⊕ AES-256-CTR_K(0);  check canary = 0^16
and the length field; otherwise raise Reject(INTEGRITY).

This is the package-transform idea of Rivest (FSE 1997) with the key-hiding
last block in the style of Boyko's OAEP analysis (CRYPTO 1999); Desai (CRYPTO
2000) analyses CTR-based variants. It is a *computational* AONT. It is NOT
information-theoretically secure.

Security statement (ANALYTICALLY DERIVED, proof sketch in
docs/fragmentation_aont.md): modelling SHA-256 as a random oracle and AES-256
as a PRF, an adversary that is missing at least b bits of Y that it cannot
compute from the rest of its view, and that makes q oracle queries, learns
information about M with advantage at most  q·2^(−b) + Adv_prf(AES-256).

What it adds beyond the record-layer AEAD: the AEAD already hides M from anyone
without the session key. The AONT only matters if the session key is later
exposed (endpoint compromise or a future break of the key exchange in a
harvest-now-decrypt-later setting): an adversary who recorded fewer than k of
the n fragments of a message still cannot recover any part of it. Within the
on-path model where the adversary records every packet, it adds nothing.
"""
import hashlib
import os
import struct

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .errors import Reject, Reason

KEY_LEN = 32
CANARY = b"\x00" * 16
OVERHEAD = 4 + len(CANARY) + KEY_LEN          # bytes added to |M|


def _ctr(key: bytes, data: bytes) -> bytes:
    enc = Cipher(algorithms.AES(key), modes.CTR(b"\x00" * 16)).encryptor()
    return enc.update(data) + enc.finalize()


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def transform(message: bytes, key: bytes = None) -> bytes:
    if len(message) >= 1 << 32:
        raise ValueError("message too long")
    k = key if key is not None else os.urandom(KEY_LEN)
    x = struct.pack(">I", len(message)) + message + CANARY
    c = _ctr(k, x)
    t = _xor(k, hashlib.sha256(c).digest())
    return c + t


def inverse(y: bytes) -> bytes:
    if len(y) < OVERHEAD:
        raise Reject(Reason.INTEGRITY, "AONT block too short")
    c, t = y[:-KEY_LEN], y[-KEY_LEN:]
    k = _xor(t, hashlib.sha256(c).digest())
    x = _ctr(k, c)
    (n,) = struct.unpack(">I", x[:4])
    if x[-16:] != CANARY or n != len(x) - 4 - 16:
        raise Reject(Reason.INTEGRITY, "AONT canary/length check failed")
    return x[4:4 + n]
