import hashlib

class SignatureEngine:
    """
    Lightweight deterministic signature abstraction.
    """

    def sign(self, data: bytes, key: bytes) -> bytes:
        return hashlib.sha256(key + data).digest()

    def verify(self, data: bytes, signature: bytes, key: bytes) -> bool:
        return hashlib.sha256(key + data).digest() == signature
