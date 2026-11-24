#!/usr/bin/env bash

send_packet() {
    local loss=$1 crypto=$2 replay=$3 delay_only=$4

    latency=$(awk "BEGIN {print 1 + $crypto*1.5 + $delay_only*2}")
    effective_loss=$(awk "BEGIN {print $loss * (1 - 0.3*$crypto)}")

    if [[ "$replay" -eq 1 ]]; then
        recv=1
    else
        recv=$(awk "BEGIN {print (rand() < $effective_loss ? 0 : 1)}")
    fi

    cost=$(awk "BEGIN {print 1 + $crypto*4 + $latency}")
    echo "$recv $latency $cost"
}
