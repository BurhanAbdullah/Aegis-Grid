#!/bin/bash

rm -f validation_report.txt

echo "Differentiated Model Validation Report" >> validation_report.txt
echo "======================================" >> validation_report.txt

MODELS=("AegisGrid" "EncryptedOnly" "IEC62351" "IDSAdaptive")

for m in "${MODELS[@]}"; do
    echo "Processing $m..."

    lat=$(python3 run_live_tests.py "$m" "LatencyFeasible")
    leak=$(python3 run_live_tests.py "$m" "TrafficLeakage")

    echo "System: $m" >> validation_report.txt
    echo "  - Latency Score: $lat" >> validation_report.txt
    echo "  - Leakage Risk:  $leak" >> validation_report.txt
    echo "--------------------------------------" >> validation_report.txt
done

cat validation_report.txt
