import time
class AgentV2:
    """Proprietary Post-Quantum Time-Bounded Agent Logic"""
    TIME_WINDOW = 2.0
    def __init__(self, key):
        self.key = key
        self.locked = False
    def is_fresh(self, ts):
        return (time.time() - ts) < self.TIME_WINDOW
