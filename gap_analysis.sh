#!/bin/bash

BASE_LAT=0.9

LIVE_LAT=$(awk '
/System: AegisGrid/ {flag=1}
/Latency Score:/ && flag {print $NF; exit}
' validation_report.txt)

echo "-------------------------------------------------------"
echo "AegisGrid Performance Validation"
echo "Baseline Latency: $BASE_LAT"
echo "Measured Latency: $LIVE_LAT"

python3 - <<PY
base = float("$BASE_LAT")
live = float("$LIVE_LAT")
diff = abs(live - base)

print(f"Absolute Difference: {diff:.4f}")

if diff < 0.05:
    print("STATUS: SUCCESS - Model matches the baseline.")
else:
    print("STATUS: ALERT - Performance deviation detected!")
PY

echo "-------------------------------------------------------"
