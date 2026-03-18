import hashlib
import hmac
import os


# ── HKDF (RFC 5869) — pure stdlib, no extra dependency ───────────────────────
# Replaces the previous chained SHA-256 which had no salt or domain separation.
# Uses HMAC-SHA-256 for extract + expand steps.
# Provides proper key separation per layer (domain binding via `info`).

def _hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    """HKDF-Extract: salt + input key material → pseudorandom key."""
    if not salt:
        salt = bytes(32)
    return hmac.new(salt, ikm, hashlib.sha256).digest()


def _hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    """HKDF-Expand: pseudorandom key → output key material of `length` bytes."""
    okm = b''
    t = b''
    counter = 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        okm += t
        counter += 1
    return okm[:length]


def derive_layer_keys(master_key: bytes, nonce: bytes, layers: int = 7) -> list:
    """
    Derive `layers` independent 32-byte keys from master_key + nonce.

    Uses HKDF (RFC 5869) with per-layer domain separation via info string.
    Each key is cryptographically independent — compromise of one layer key
    does not reveal others (forward/backward key separation).

    This replaces the previous chained SHA-256 construction which lacked
    salt and domain separation, violating the IND-CCA2 assumption in L1.

    Parameters
    ----------
    master_key : bytes   Master secret (32 bytes recommended)
    nonce      : bytes   Per-session nonce (msg_id or os.urandom(16))
    layers     : int     Number of layer keys to derive (default 7 = L1..L7)

    Returns
    -------
    list of `layers` 32-byte keys, one per security layer.
    """
    # Extract: combine master_key and nonce into a single PRK
    prk = _hkdf_extract(salt=nonce, ikm=master_key)

    # Expand: one key per layer with domain-separated info string
    keys = []
    for i in range(layers):
        info = f"aegis-grid-layer-{i}".encode()
        layer_key = _hkdf_expand(prk, info, length=32)
        keys.append(layer_key)

    return keys


def derive_single_key(master_key: bytes, nonce: bytes, layer_id: int) -> bytes:
    """
    Derive a single layer key — drop-in replacement for SecureAgent.get_layer_key().
    Keeps the per-layer call interface while using proper HKDF internally.
    """
    prk = _hkdf_extract(salt=nonce, ikm=master_key)
    info = f"aegis-grid-layer-{layer_id}".encode()
    return _hkdf_expand(prk, info, length=32)
