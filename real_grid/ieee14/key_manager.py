import time, hmac, hashlib, secrets

class GridKeyManager:
    def __init__(self, lifetime):
        self.lifetime = lifetime
        self.keys = {}

    def issue(self, node):
        k = secrets.token_bytes(32)
        self.keys[node] = (k, time.time())
        return k

    def valid(self, node):
        if node not in self.keys:
            return False
        _, t = self.keys[node]
        return (time.time() - t) <= self.lifetime

    def sign(self, key, msg):
        return hmac.new(key, msg.encode(), hashlib.sha256).hexdigest()

    def verify(self, key, msg, sig):
        return hmac.compare_digest(
            self.sign(key, msg), sig
        )
