import random

def run_all(agent, gen_fn, rec_fn):
    print("\n=== Aegis-Grid: Verified Results ===")

    for loss in [0.1, 0.2, 0.3, 0.4]:
        success = 0

        for _ in range(100):
            agent.locked = False
            agent.observe(loss)

            packets = gen_fn(agent, b"DATA", 0.5)
            kept = [p for p in packets if random.random() > loss]

            if rec_fn(kept, agent):
                success += 1

        print(f"Loss {int(loss*100)}% | Threshold {agent.threshold:2} | Success {success/100:.3f}")
