import random
from core.fragmentation import aont_fragment, aont_reconstruct

def run_all(agent, traffic_fn=None, receiver_fn=None):
    print("\n=== Aegis-Grid: v1.3 Triple-Pillar Validation ===")

    for loss in [0.1, 0.2, 0.3, 0.4]:
        success, trials = 0, 100

        for _ in range(trials):
            from agents.secure_agent import SecureAgent

            trial_agent = SecureAgent(agent.master_key)
            trial_agent.observe(loss)

            data = b"POWER_GRID_CMD"

            fragments = aont_fragment(data, trial_agent.fragment_count)

            received = [
                f for f in fragments if random.random() > loss
            ]

            if len(received) == len(fragments):
                recovered = aont_reconstruct(received)
                if recovered == data:
                    success += 1

        print(f"Loss {int(loss*100):2d}% | Success {success/trials:.3f}")
