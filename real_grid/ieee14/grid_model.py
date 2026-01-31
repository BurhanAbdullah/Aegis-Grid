import csv

class IEEE14Grid:
    def __init__(self, pmu_files):
        self.data = {}
        for node, path in pmu_files.items():
            with open(path) as f:
                self.data[node] = list(csv.DictReader(f))
        self.i = 0

    def next(self):
        out = {}
        for node, rows in self.data.items():
            r = rows[self.i]
            out[node] = {
                "freq": float(r["freq"]),
                "voltage": float(r["voltage"]),
                "angle": float(r["angle"]),
                "ts": float(r["timestamp"])
            }
        self.i = min(self.i + 1, len(next(iter(self.data.values()))) - 1)
        return out
