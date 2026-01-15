class LearningAgent:
    """
    Online adaptive security agent.
    Uses exponential moving averages to adapt
    fragmentation and dummy ratios.
    """

    def __init__(self):
        self.loss_ema = 0.0
        self.delay_ema = 0.0
        self.alpha = 0.2  # learning rate

        self.fragment_count = 8
        self.dummy_ratio = 1.0

    def observe(self, loss, delay):
        self.loss_ema = (1 - self.alpha) * self.loss_ema + self.alpha * loss
        self.delay_ema = (1 - self.alpha) * self.delay_ema + self.alpha * delay

    def act(self):
        threat = min(1.0, self.loss_ema + self.delay_ema)

        # Adaptive policy (stable + bounded)
        self.fragment_count = 8 + int(6 * threat)
        self.dummy_ratio = 1.0 + 2.0 * threat

        return self.fragment_count, self.dummy_ratio
