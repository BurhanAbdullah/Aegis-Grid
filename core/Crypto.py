class CryptoEngine:
    """
    Abstract cryptographic interface.
    Concrete implementations may use post-quantum primitives.
    """

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError
