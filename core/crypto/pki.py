from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class GridIdentity:
    @staticmethod
    def verify_node(message, signature, public_key):
        """Obj 12: Certification Verification (Pillar 3 Identity)"""
        h = SHA256.new(message)
        try:
            pkcs1_15.new(public_key).verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False

def generate_authority_keys():
    """Generates the Root of Trust for the Grid"""
    key = RSA.generate(2048)
    return key, key.publickey()
