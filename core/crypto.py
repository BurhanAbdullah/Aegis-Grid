import hashlib
import hmac

class CryptoEngine:
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        return hashlib.sha256(key + data).digest()

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        return data

    def mac(self, data: bytes, key: bytes) -> bytes:
        return hmac.new(key, data, hashlib.sha256).digest()

    def verify_mac(self, data: bytes, mac: bytes, key: bytes) -> bool:
        return hmac.compare_digest(
            self.mac(data, key),
            mac
        )
