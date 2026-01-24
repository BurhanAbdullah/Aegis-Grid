#!/bin/bash

MODELS=("AegisGrid" "EncryptedOnly" "IEC62351" "IDSAdaptive")
METRICS=("LatencyFeasible" "PartialReconstructionRisk" "TrafficLeakage" "FailSecure")

echo "======================================================="
echo "        SYSTEM PERFORMANCE VALIDATION START            "
echo "======================================================="

for model in "${MODELS[@]}"; do
    echo "[TESTING MODEL: $model]"
    for metric in "${METRICS[@]}"; do
        # Capture the output of the runner
        result=$(./model_runner --system="$model" --metric="$metric")
        
        # Simple threshold check to see if it's "better" than a 0.5 baseline
        status="PASS"
        if (( $(echo "$result < 0.5" | bc -l) )); then
            status="WARN (LOW SCORE)"
        fi
        
        printf "  %-25s | Score: %s | Status: %s\n" "$metric" "$result" "$status"
    done
    echo "-------------------------------------------------------"
done
