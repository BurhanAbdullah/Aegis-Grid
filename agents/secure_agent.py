from agents.learning_agent import LearningAgent

class SecureAgent:
    def __init__(self, master_key):
        self.master_key = master_key
        self.learner = LearningAgent()

    @property
    def fragment_count(self):
        return self.learner.fragment_count

    @property
    def dummy_ratio(self):
        return self.learner.dummy_ratio

    def update(self, loss, delay):
        self.learner.observe(loss, delay)
        self.learner.act()
