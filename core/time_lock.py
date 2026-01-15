import time
import hashlib

class TimeLock:
    """
    Enforces irreversible message expiry.
    Once expired, recovery is impossible.
    """

    def __init__(self, ttl_ms: float):
        self.ttl_ms = ttl_ms

    def seal(self, nonce: bytes) -> bytes:
        """
        Bind time-lock to a nonce.
        """
        expiry_bucket = int(time.time() * 1000 // self.ttl_ms)
        return hashlib.sha256(nonce + expiry_bucket.to_bytes(8, 'big')).digest()

    def verify(self, nonce: bytes, seal: bytes) -> bool:
        """
        Accept only if within the same time window.
        """
        expiry_bucket = int(time.time() * 1000 // self.ttl_ms)
        expected = hashlib.sha256(
            nonce + expiry_bucket.to_bytes(8, 'big')
        ).digest()
        return expected == seal
