import random
from simulation.adversary import inject_adversary
from core.fragmentation import fragment_message, reconstruct_message


def run_all(agent, traffic_fn, receiver_fn):
    """
    End-to-end simulation across four loss rates.
    Uses new fragmentation + CAP-based SecureAgent.
    Each trial creates a fresh agent to maintain stateless evaluation.
    """
    import os
    print("\n=== Aegis-Grid: v1.3 Triple-Pillar Validation ===")

    for loss in [0.1, 0.2, 0.3, 0.4]:
        success, locked, trials = 0, 0, 100

        for _ in range(trials):
            # Fresh agent per trial — stateless evaluation (matches paper)
            from agents.secure_agent import SecureAgent
            trial_agent = SecureAgent(agent.master_key)
            trial_agent.observe(loss)

            # Generate traffic using updated fragmentation
            data = b"POWER_GRID_CMD"
            key  = trial_agent.get_layer_key(0)
            n    = trial_agent.fragment_count
            rho  = trial_agent.dummy_ratio
            packets = fragment_message(data, n, rho, key)

            # Adversary: forge 30% + drop by loss rate
            packets = inject_adversary(packets, forge_ratio=0.3)
            packets = [p for p in packets if random.random() > loss]

            if trial_agent.is_locked():
                locked += 1
            else:
                recovered = reconstruct_message(packets, key)
                if recovered is not None and recovered[:len(data)] == data:
                    success += 1

        print(
            f"Loss {int(loss*100):2d}% | "
            f"Success {success/trials:.3f} | "
            f"Locked {locked/trials:.3f}"
        )
