from agents.sender_agent import SenderSecurityAgent
from agents.receiver_agent import ReceiverSecurityAgent
from agents.network_agent import NetworkAgent
from protocol.sender import sender_pipeline
from protocol.receiver import receiver_pipeline
from network.adversary import apply_attacks

def run_simulation():
    net = NetworkAgent()
    sender = SenderSecurityAgent()
    receiver = ReceiverSecurityAgent()

    threat = net.observe(0.3, 0.2, 0.1)

    packets = sender_pipeline(
        "Shutdown Station A",
        sender,
        threat
    )

    attacked = apply_attacks(packets, drop_rate=0.3, delay=True)
    return receiver_pipeline(attacked, receiver, 30)
