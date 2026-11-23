class ReceiverSecurityAgent:
    def verify(self, packets):
        return all(p.auth_tag == "VALID" for p in packets)
receiver_agent.py
