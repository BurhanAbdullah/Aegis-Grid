import time
from key_manager import GridKeyManager

class SevenLayer:
    def __init__(self):
        self.keys = GridKeyManager(120)

    def eval(self, p, g):
        L = {}

        L[1] = self.keys.valid(p["node"])
        L[2] = p["size"] <= 256
        L[3] = self.keys.verify(
            self.keys.keys[p["node"]][0],
            p["payload"],
            p["sig"]
        )
        L[4] = (time.time() - p["ts"]) * 1000 <= 100
        L[5] = p["pressure"] < 5.0

        measurement = g.parse(p["payload"])
        L[6] = g.safe(measurement)

        L[7] = p["role"] == "PMU"

        return all(L.values()), L
