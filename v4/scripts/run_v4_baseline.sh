#!/usr/bin/env bash

source ./v4/scripts/microgrid_state.sh
source ./v4/scripts/comm_channel.sh
source ./v4/scripts/attacks.sh

OUT="v4/data/v4_baseline.dat"
echo "#t loss entropy freq volt stab" > "$OUT"

STATE=$(init_microgrid)

for t in $(seq 1 100); do
    LOSS=$(attack_loss $t)
    ENTROPY=$(attack_entropy $t)

    read FREQ VOLT STAB <<< "$STATE"
    read RECV LAT COST <<< $(send_packet "$LOSS" 0)

    STATE=$(update_physical "$FREQ" "$VOLT" "$STAB" "$RECV" "$ENTROPY" "$LAT")
    echo "$t $LOSS $ENTROPY $STATE" >> "$OUT"
done
