import random
from simulation.adversary import inject_adversary

def run_all(agent, traffic_fn, receiver_fn):
    print("\n=== Aegis-Grid: Final Pillar 3 Validation ===")
    for loss in [0.1, 0.2, 0.3, 0.4]:
        success, locked = 0, 0
        for _ in range(100):
            agent.attack_pressure = 0 
            agent.locked = False
            agent.observe(loss) 
            
            # 1. Generate normal traffic
            packets = traffic_fn(agent, b"POWER_GRID_CMD", 0.2)
            
            # 2. Inject Pillar 3 Adversary (30% Forgery)
            attacked_packets = inject_adversary(packets, forge_ratio=0.3)
            
            # 3. Simulate real network loss
            kept = [p for p in attacked_packets if random.random() > loss]
            
            if receiver_fn(kept, agent):
                success += 1
            if agent.is_locked():
                locked += 1
                
        print(f"Loss {int(loss*100)}% | Success {success/100:.3f} | Locked {locked/100:.3f}")
