from simulation.run_experiments import run_all
from agents.secure_agent import SecureAgent
from protocol.sender import generate_traffic
from protocol.receiver import receive_and_reconstruct
from Crypto.Random import get_random_bytes

if __name__ == "__main__":
    key = get_random_bytes(16)
    agent = SecureAgent(key)

    run_all(
        agent=agent,
        generate_fn=generate_traffic,
        receive_fn=receive_and_reconstruct
    )
from simulation.run_experiments import run_all
from protocol.sender import generate_traffic
from protocol.receiver import receive_and_reconstruct
from agents.secure_agent import SecureAgent
from Crypto.Random import get_random_bytes

if __name__ == "__main__":
    key = get_random_bytes(16)
    agent = SecureAgent(key)

    run_all(
        agent=agent,
        generate_fn=generate_traffic,
        receive_fn=receive_and_reconstruct
    )
