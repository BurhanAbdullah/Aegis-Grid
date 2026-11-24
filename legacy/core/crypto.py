import hashlib

class CryptoEngine:
    """
    Cryptographic abstraction.
    This is intentionally symmetric and lightweight.
    Replace with post-quantum primitives in production.
    """

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        return hashlib.sha256(key + data).digest()

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        # Abstract symmetric placeholder
        return data
