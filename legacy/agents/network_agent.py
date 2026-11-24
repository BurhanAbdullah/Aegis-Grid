class NetworkAgent:
    def observe(self, congestion, loss, flood):
        return min(1.0, congestion + loss + flood)
