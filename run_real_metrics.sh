#!/bin/bash

MODELS=("AegisGrid" "EncryptedOnly" "IEC62351" "IDSAdaptive")
METRICS=("LatencyFeasible" "TrafficLeakage")

echo "======================================================="
echo "        LIVE MODEL EXECUTION & VERIFICATION            "
echo "======================================================="

for model in "${MODELS[@]}"; do
    echo "[RUNNING: $model]"
    for metric in "${METRICS[@]}"; do
        # Execute the python logic directly
        result=$(python3 run_live_tests.py "$metric")
        
        # Compare against your previous "Model-Based" claims
        echo "  $metric -> Measured: $result"
    done
    echo "-------------------------------------------------------"
done
