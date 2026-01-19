#!/usr/bin/env bash

source v4/scripts/microgrid_dual.sh
source v4/scripts/channel_attack.sh
source v4/scripts/agent_vs_baseline.sh
source v4/scripts/attacks.sh

OUT="v4/data/v4_compare.dat"
echo "#t loss entropy cr_freq cr_volt cr_stab ss_freq ss_volt ss_stab mode" > "$OUT"

CR=$(init_grid)
SS=$(init_grid)

for t in $(seq 1 100); do
    LOSS=$(attack_loss $t)
    ENTROPY=$(attack_entropy $t)

    REPLAY=0
    DELAY=0
    [[ $t -ge 55 && $t -le 70 ]] && DELAY=1
    [[ $t -ge 65 && $t -le 75 ]] && REPLAY=1

    read CF CV CS <<< "$CR"
    read SF SV SS_ST <<< "$SS"

    read MODE CRYPTO <<< $(agent_decide "$LOSS" "$ENTROPY" "$CF" "$CV" "$CS")

    read RECV LAT COST <<< $(send_packet "$LOSS" "$CRYPTO" "$REPLAY" "$DELAY")

    CR=$(update_grid "$CF" "$CV" "$CS" "$RECV" "$ENTROPY" "$LAT")
    SS=$(update_grid "$SF" "$SV" "$SS_ST" "$RECV" "$ENTROPY" "$LAT")

    read CF CV CS <<< "$CR"
    read SF SV SS_ST <<< "$SS"

    echo "$t $LOSS $ENTROPY $CF $CV $CS $SF $SV $SS_ST $MODE" >> "$OUT"
done
