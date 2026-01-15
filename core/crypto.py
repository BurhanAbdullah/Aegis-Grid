import hashlib
import hmac

class CryptoEngine:
    """
    Abstract cryptographic engine.
    Replace with PQ signatures in production.
    """

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        return hashlib.sha256(key + data).digest()

    def sign(self, data: bytes, key: bytes) -> bytes:
        return hmac.new(key, data, hashlib.sha256).digest()

    def verify(self, data: bytes, sig: bytes, key: bytes) -> bool:
        return hmac.compare_digest(
            hmac.new(key, data, hashlib.sha256).digest(),
            sig
        )
