#!/usr/bin/env bash
set -e

pip install --quiet pandapower numba pandas

OUTDIR="results_v3.3"
mkdir -p "$OUTDIR"

python <<'PYCODE'
import time, random
import pandas as pd
import pandapower.networks as pn
import pandapower as pp

PMU_RATE = 30
VALIDITY_WINDOW = 0.05
NETWORK_DELAY = 0.06
PACKET_LOSS = 0.2
STEPS = 30

net = pn.case39()
pp.runpp(net)

accepted = 0

for _ in range(STEPS):
    send = time.time()
    delivered = False

    for _ in net.bus.index:
        if random.random() < PACKET_LOSS:
            continue
        time.sleep(NETWORK_DELAY)
        if time.time() - send <= VALIDITY_WINDOW:
            delivered = True
            break

    if delivered:
        accepted += 1

    time.sleep(1 / PMU_RATE)

df = pd.DataFrame([{
    "system": "IEEE-39",
    "acceptance_ratio": accepted / STEPS
}])

df.to_csv("results_v3.3/ieee39_results.csv", index=False)
print(df)
PYCODE
