from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class GridCA:
    def __init__(self):
        self._key = RSA.generate(2048)
        self.public_key = self._key.publickey()
    def sign(self, data):
        h = SHA256.new(data)
        return pkcs1_15.new(self._key).sign(h)
    def verify(self, data, sig):
        h = SHA256.new(data)
        try: pkcs1_15.new(self.public_key).verify(h, sig); return True
        except: return False
ROOT_CA = GridCA()
