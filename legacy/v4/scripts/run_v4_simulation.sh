#!/usr/bin/env bash

source ./v4/scripts/microgrid_state.sh
source ./v4/scripts/comm_channel.sh
source ./v4/scripts/attacks.sh
source ./v4/scripts/agent.sh

OUT="v4/data/v4_microgrid_results.dat"
echo "#t loss entropy freq volt stab crypto latency cost recv state" > "$OUT"

STATE=$(init_microgrid)
TOTAL_COST=0

for t in $(seq 1 100); do
    LOSS=$(attack_loss $t)
    ENTROPY=$(attack_entropy $t)

    read FREQ VOLT STAB <<< "$STATE"
    read MODE CRYPTO <<< $(agent_decide "$LOSS" "$ENTROPY" "$FREQ" "$VOLT" "$STAB")

    read RECV LAT COST <<< $(send_packet "$LOSS" "$CRYPTO")
    TOTAL_COST=$(awk "BEGIN {print $TOTAL_COST + $COST}")

    STATE=$(update_physical "$FREQ" "$VOLT" "$STAB" "$RECV" "$ENTROPY" "$LAT")

    echo "$t $LOSS $ENTROPY $FREQ $VOLT $STAB $CRYPTO $LAT $COST $RECV $MODE" >> "$OUT"

    [[ "$MODE" == "FAIL_SECURE" ]] && break
done

echo "TOTAL_COST=$TOTAL_COST" > v4/logs/summary.txt
