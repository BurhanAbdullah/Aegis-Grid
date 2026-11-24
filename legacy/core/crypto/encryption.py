from Crypto.Cipher import AES

class AegisCrypt:
    def __init__(self, key):
        self.key = key

    def seal(self, data):
        """Layer 1: Symmetric Encryption Shell"""
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return {"c": ciphertext, "n": cipher.nonce, "t": tag}

    def open(self, bundle):
        """Final Layer: Re-assembly Decryption"""
        try:
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=bundle["n"])
            return cipher.decrypt_and_verify(bundle["c"], bundle["t"])
        except:
            return None
