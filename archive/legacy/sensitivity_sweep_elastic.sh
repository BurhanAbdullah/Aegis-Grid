#!/usr/bin/env bash

RESULTS="sensitivity_matrix_elastic.csv"
echo "intensity,mode,total_loss,total_cost,status" > "$RESULTS"

echo "=== AEGIS-GRID ELASTIC MITIGATION SWEEP ==="

FAIL_THRESHOLD=18

BASE_COST=1.0
MID_COST=1.8
HIGH_COST=2.5

NO_MIT_LOSS=1.0       # no mitigation (raw loss)
MID_MIT_LOSS=0.5      # partial mitigation
STRONG_MIT_LOSS=0.2   # strong mitigation

for intensity in $(seq 0.4 0.1 1.3); do
  for mode in FIXED_MITIGATION ELASTIC_MITIGATION; do

    C_LOSS=0
    TOTAL_COST=0
    STATUS="OPERATIONAL"

    for t in {1..100}; do
      # --- base attack ---
      if (( t >= 40 && t <= 70 )); then
        RAW_LOSS=$(awk "BEGIN {print 0.05 + ($t-40)*($intensity/15)}")
      else
        RAW_LOSS=0.05
      fi

      # --- agent decision ---
      if [[ "$mode" == "FIXED_MITIGATION" ]]; then
        LOSS=$STRONG_MIT_LOSS
        COST=$HIGH_COST

      else
        PRESSURE=$(awk "BEGIN {print $C_LOSS/$FAIL_THRESHOLD}")

        if (( $(awk "BEGIN {print ($PRESSURE<0.4)}") )); then
          LOSS=$RAW_LOSS
          COST=$BASE_COST
        elif (( $(awk "BEGIN {print ($PRESSURE<0.7)}") )); then
          LOSS=$(awk "BEGIN {print $RAW_LOSS*$MID_MIT_LOSS}")
          COST=$MID_COST
        elif (( $(awk "BEGIN {print ($PRESSURE<=1.0)}") )); then
          LOSS=$(awk "BEGIN {print $RAW_LOSS*$STRONG_MIT_LOSS}")
          COST=$HIGH_COST
        else
          STATUS="LOCKED_DOWN"
          break
        fi
      fi

      C_LOSS=$(awk "BEGIN {print $C_LOSS+$LOSS}")
      TOTAL_COST=$(awk "BEGIN {print $TOTAL_COST+$COST}")

      if (( $(awk "BEGIN {print ($C_LOSS>$FAIL_THRESHOLD)}") )); then
        STATUS="LOCKED_DOWN"
        break
      fi
    done

    printf "%.1f,%s,%.3f,%.1f,%s\n" \
      "$intensity" "$mode" "$C_LOSS" "$TOTAL_COST" "$STATUS" >> "$RESULTS"

    printf "Intensity %.1f | %-18s | Loss %.3f | Cost %.1f | %s\n" \
      "$intensity" "$mode" "$C_LOSS" "$TOTAL_COST" "$STATUS"

  done
done

echo "-------------------------------------------"
echo "Elastic mitigation matrix saved to $RESULTS"
