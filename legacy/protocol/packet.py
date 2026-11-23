import time

class SecurePacket:
    def __init__(self, ciphertext, nonce, tag, cert, timestamp):
        self.ciphertext = ciphertext
        self.nonce = nonce
        self.tag = tag
        self.cert = cert
        self.timestamp = timestamp
