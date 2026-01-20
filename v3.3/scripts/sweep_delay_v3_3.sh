#!/usr/bin/env bash
set -e

pip install --quiet pandapower numba pandas

OUTDIR="results_v3.3"
mkdir -p "$OUTDIR"

python <<'PYCODE'
import time, random
import pandas as pd
import pandapower as pp
import pandapower.networks as pn

PMU_RATE = 30
VALIDITY_WINDOW = 0.05
PACKET_LOSS = 0.2
STEPS = 50

delays = [0.0, 0.02, 0.04, 0.06, 0.08, 0.1]
results = []

net = pn.case14()

for delay in delays:
    accepted = 0
    total = 0

    for _ in range(STEPS):
        pp.runpp(net)
        send = time.time()
        delivered = False

        for _ in net.bus.index:
            if random.random() < PACKET_LOSS:
                continue
            time.sleep(delay)
            if time.time() - send <= VALIDITY_WINDOW:
                delivered = True
                break

        if delivered:
            accepted += 1
        total += 1

        time.sleep(1 / PMU_RATE)

    results.append({
        "delay_ms": int(delay * 1000),
        "acceptance_ratio": accepted / total
    })

df = pd.DataFrame(results)
df.to_csv("results_v3.3/delay_sweep.csv", index=False)
print(df)
PYCODE
