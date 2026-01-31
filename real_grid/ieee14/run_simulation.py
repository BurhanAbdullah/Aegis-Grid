import time
from grid_model import IEEE14Grid
from seven_layer_model import SevenLayer

grid = IEEE14Grid({
    "PMU_3": "../pmu_data/ieee14/PMU_3.csv",
    "PMU_6": "../pmu_data/ieee14/PMU_3.csv",
    "PMU_9": "../pmu_data/ieee14/PMU_3.csv",
})

aegis = SevenLayer()

node = "PMU_3"
key = aegis.keys.issue(node)
pressure = 1.0

for step in range(4):
    grid_meas = grid.next()
    grid_ts = list(grid_meas.values())[0]["ts"]

    packet = {
        "node": node,
        "payload": f"STEP={step}",
        "sig": aegis.keys.sign(key, f"STEP={step}"),
        "ts": grid_ts,
        "size": 128,
        "pressure": pressure,
        "role": "PMU",
        "msg_type": "MEASUREMENT"
    }

    ok, layers = aegis.eval(packet, grid_meas, grid_ts)
    pressure = packet["pressure"]

    print(f"\nStep {step} → {'ACCEPTED' if ok else 'REJECTED'} | Pressure={pressure}")
    for k, v in layers.items():
        print(f"  L{k}: {v}")
