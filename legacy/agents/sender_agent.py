class SenderSecurityAgent:
    def adapt(self, threat_level):
        return {
            "fragments": 10 + int(threat_level * 5),
            "dummy_ratio": min(2.0, 0.5 + threat_level)
        }
