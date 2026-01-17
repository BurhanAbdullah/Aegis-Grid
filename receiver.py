from collections import deque

class Receiver:
    def __init__(self, agent):
        self.agent = agent

        self.epoch_size = 10
        self.epoch_invalid = 0
        self.epoch_total = 0

        self.bad_epochs = deque(maxlen=3)

    def receive(self, fragments, forged=False, replay=False):
        if self.agent.locked:
            return

        self.epoch_total += len(fragments)

        if forged:
            self.epoch_invalid += len(fragments)

        if self.epoch_total >= self.epoch_size:
            ratio = self.epoch_invalid / self.epoch_total
            if ratio > self.agent.max_invalid_ratio:
                print(f"[SECURITY] FORGERY sustained {self.epoch_invalid}/{self.epoch_total} → NODE LOCKED")
                self.agent.locked = True

            self.epoch_invalid = 0
            self.epoch_total = 0
