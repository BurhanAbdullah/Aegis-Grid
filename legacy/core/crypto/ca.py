from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class GridCA:
    """V1 Classical RSA-2048 Certification Authority"""
    def __init__(self):
        self._key = RSA.generate(2048)
        self.public_key = self._key.publickey()

    def sign(self, data: bytes) -> bytes:
        h = SHA256.new(data)
        return pkcs1_15.new(self._key).sign(h)

    def verify(self, data: bytes, signature: bytes) -> bool:
        h = SHA256.new(data)
        try:
            pkcs1_15.new(self.public_key).verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False

ROOT_CA = GridCA()
