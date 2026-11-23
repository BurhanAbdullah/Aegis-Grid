import hmac
import hashlib

def compute_mac(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()

def verify_mac(key: bytes, data: bytes, tag: bytes) -> bool:
    return hmac.compare_digest(
        hmac.new(key, data, hashlib.sha256).digest(),
        tag
    )
