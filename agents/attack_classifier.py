class AttackClassifier:
    """
    Classifies attack type based on observed symptoms.
    """

    def __init__(self):
        self.loss_score = 0.0
        self.delay_score = 0.0
        self.forgery_score = 0.0

    def observe_loss(self, loss_rate: float):
        self.loss_score = min(1.0, self.loss_score + loss_rate)

    def observe_delay(self, delay_ms: float):
        if delay_ms > 20:
            self.delay_score = min(1.0, self.delay_score + delay_ms / 100.0)

    def observe_forgery(self):
        self.forgery_score = 1.0

    def classify(self) -> str:
        if self.forgery_score > 0.0:
            return "FORGERY"
        if self.loss_score > 0.5 and self.delay_score > 0.3:
            return "MIXED"
        if self.loss_score > self.delay_score:
            return "LOSS"
        if self.delay_score > 0.3:
            return "DELAY"
        return "NORMAL"
