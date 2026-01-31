class IEEE14Grid:
    def parse(self, payload):
        parts = dict(x.split("=") for x in payload.split(";"))
        return {
            "freq": float(parts["F"]),
            "voltage": float(parts["V"])
        }

    def safe(self, measurement):
        return (
            49.5 <= measurement["freq"] <= 50.5 and
            0.95 <= measurement["voltage"] <= 1.05
        )
