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
NETWORK_DELAY = 0.08
PACKET_LOSS = 0.2
STEPS = 50

modes = ["baseline", "fail_secure"]
records = []

net = pn.case14()

for mode in modes:
    accepted = 0

    for _ in range(STEPS):
        pp.runpp(net)
        send = time.time()
        delivered = False

        for _ in net.bus.index:
            if random.random() < PACKET_LOSS:
                continue
            time.sleep(NETWORK_DELAY)
            if mode == "baseline":
                delivered = True
                break
            elif time.time() - send <= VALIDITY_WINDOW:
                delivered = True
                break

        if delivered:
            accepted += 1

        time.sleep(1 / PMU_RATE)

    records.append({
        "mode": mode,
        "acceptance_ratio": accepted / STEPS
    })

df = pd.DataFrame(records)
df.to_csv("results_v3.3/baseline_vs_failsecure.csv", index=False)
print(df)
PYCODE
