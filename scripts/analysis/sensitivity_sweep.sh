#!/usr/bin/env bash

RESULTS="sensitivity_matrix.csv"
echo "intensity,total_loss,total_cost,status" > "$RESULTS"

echo "=== RUNNING AEGIS-GRID SENSITIVITY SWEEP ==="

FAIL_THRESHOLD=18
BASE_COST=1.0
MITIGATION_COST=2.5
AGENT_TRIGGER=50

for intensity in $(seq 0.4 0.1 1.3); do
    C_LOSS=0
    TOTAL_COST=0
    STATUS="OPERATIONAL"

    for t in {1..100}; do
        # Base loss (ramp-up attack)
        if (( t >= 40 && t <= 70 )); then
            LOSS=$(awk "BEGIN {print 0.05 + ($t-40)*($intensity/15)}")
        else
            LOSS=0.05
        fi

        # Agent mitigation cost (simple model)
        if (( t >= AGENT_TRIGGER )); then
            COST=$MITIGATION_COST
        else
            COST=$BASE_COST
        fi

        C_LOSS=$(awk "BEGIN {print $C_LOSS+$LOSS}")
        TOTAL_COST=$(awk "BEGIN {print $TOTAL_COST+$COST}")

        if (( $(awk "BEGIN {print ($C_LOSS>$FAIL_THRESHOLD)}") )); then
            STATUS="LOCKED_DOWN"
        fi
    done

    printf "%.1f,%.3f,%.1f,%s\n" \
        "$intensity" "$C_LOSS" "$TOTAL_COST" "$STATUS" >> "$RESULTS"

    printf "Intensity: %.1f | Loss: %7.3f | Status: %s\n" \
        "$intensity" "$C_LOSS" "$STATUS"
done

echo "-------------------------------------------"
echo "Matrix saved to $RESULTS"
