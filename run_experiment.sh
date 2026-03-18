import random
from simulation.adversary import inject_adversary
from core.fragmentation import fragment_message, reconstruct_message


def run_all(agent, traffic_fn, receiver_fn):
    print("\n=== Aegis-Grid: v1.3 Triple-Pillar Validation ===")
    for loss in [0.1, 0.2, 0.3, 0.4]:
        success, locked, trials = 0, 0, 100
        for _ in range(trials):
            from agents.secure_agent import SecureAgent
            trial_agent = SecureAgent(agent.master_key)
            trial_agent.observe(loss)
            data = b"POWER_GRID_CMD"
            key  = trial_agent.get_layer_key(0)
            n, rho = trial_agent.fragment_count, trial_agent.dummy_ratio
            packets = fragment_message(data, n, rho, key)
            packets = inject_adversary(packets, forge_ratio=0.3)
            packets = [p for p in packets if random.random() > loss]
            if trial_agent.is_locked():
                locked += 1
            else:
                recovered = reconstruct_message(packets, key)
                if recovered is not None and recovered[:len(data)] == data:
                    success += 1
        print(f"Loss {int(loss*100):2d}% | "
              f"Success {success/trials:.3f} | "
              f"Locked {locked/trials:.3f}")
