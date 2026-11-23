"""Systematic Reed–Solomon erasure code (k-of-n, MDS) over GF(2^8).

Generator matrix G = [ I_k ; C ] with C an (n−k)×k Cauchy matrix
C[i][j] = 1 / (x_i ⊕ y_j), x_i = k + i, y_j = j (all distinct, n ≤ 256),
so every k×k submatrix of G is invertible (MDS property).
Field: GF(2^8) with primitive polynomial 0x11D.

``encode(data, k, n)`` -> n shards of equal length f = ceil(|data|/k)
``decode({index: shard}, k, n, length)`` -> data, using any k shards.
Erasure coding only tolerates *missing* shards. Corrupted shards must be
removed before decoding; in AGP/1 every shard travels in its own AEAD record,
so a modified shard is rejected and becomes an erasure.
"""
import numpy as np

from .errors import Reject, Reason

_EXP = np.zeros(512, dtype=np.uint8)
_LOG = np.zeros(256, dtype=np.int32)
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D
for _i in range(255, 512):
    _EXP[_i] = _EXP[_i - 255]


def gf_mul(a, b):
    a = np.asarray(a, dtype=np.int32); b = np.asarray(b, dtype=np.int32)
    out = _EXP[(_LOG[a] + _LOG[b]) % 255]
    return np.where((a == 0) | (b == 0), 0, out).astype(np.uint8)


def gf_inv(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError
    return int(_EXP[255 - _LOG[a]])


def _mat_vec(mat, shards):
    """mat: (r×k) uint8, shards: (k×f) uint8 -> (r×f)."""
    r, k = mat.shape
    out = np.zeros((r, shards.shape[1]), dtype=np.uint8)
    for i in range(r):
        acc = np.zeros(shards.shape[1], dtype=np.uint8)
        for j in range(k):
            if mat[i, j]:
                acc ^= gf_mul(mat[i, j], shards[j])
        out[i] = acc
    return out


def cauchy(k: int, n: int) -> np.ndarray:
    m = n - k
    c = np.zeros((m, k), dtype=np.uint8)
    for i in range(m):
        for j in range(k):
            c[i, j] = gf_inv((k + i) ^ j)
    return c


def generator(k: int, n: int) -> np.ndarray:
    if not (1 <= k <= n <= 256):
        raise ValueError("require 1 <= k <= n <= 256")
    return np.vstack([np.eye(k, dtype=np.uint8), cauchy(k, n)])


def _invert(m: np.ndarray) -> np.ndarray:
    k = m.shape[0]
    a = np.concatenate([m.copy(), np.eye(k, dtype=np.uint8)], axis=1)
    for col in range(k):
        piv = next((r for r in range(col, k) if a[r, col]), None)
        if piv is None:
            raise Reject(Reason.INTEGRITY, "singular decoding matrix")
        a[[col, piv]] = a[[piv, col]]
        a[col] = gf_mul(gf_inv(int(a[col, col])), a[col])
        for r in range(k):
            if r != col and a[r, col]:
                a[r] ^= gf_mul(a[r, col], a[col])
    return a[:, k:]


def encode(data: bytes, k: int, n: int) -> list:
    f = max(1, -(-len(data) // k))
    buf = np.frombuffer(data + b"\x00" * (f * k - len(data)), dtype=np.uint8).reshape(k, f)
    if n == k:
        return [bytes(r) for r in buf]
    parity = _mat_vec(cauchy(k, n), buf)
    return [bytes(r) for r in buf] + [bytes(r) for r in parity]


def decode(shards: dict, k: int, n: int, length: int) -> bytes:
    if len(shards) < k:
        raise Reject(Reason.INCOMPLETE, f"{len(shards)} of {k} shards")
    idx = sorted(shards)[:k]
    if any(i < 0 or i >= n for i in idx):
        raise Reject(Reason.MALFORMED, "shard index out of range")
    sizes = {len(shards[i]) for i in idx}
    if len(sizes) != 1:
        raise Reject(Reason.MALFORMED, "unequal shard sizes")
    f = sizes.pop()
    if length > f * k:
        raise Reject(Reason.MALFORMED, "length exceeds shard capacity")
    if idx == list(range(k)):
        data = b"".join(shards[i] for i in idx)
    else:
        sub = generator(k, n)[idx]
        inv = _invert(sub)
        got = np.stack([np.frombuffer(shards[i], dtype=np.uint8) for i in idx])
        data = _mat_vec(inv, got).tobytes()
    return data[:length]
