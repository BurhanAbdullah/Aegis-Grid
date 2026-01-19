#!/usr/bin/env bash

send_packet() {
    local loss=$1 crypto=$2

    latency=$(awk "BEGIN {print 1 + $crypto*1.5}")
    effective_loss=$(awk "BEGIN {print $loss * (1 - 0.25*$crypto)}")

    recv=$(awk "BEGIN {print (rand() < $effective_loss ? 0 : 1)}")
    cost=$(awk "BEGIN {print 1 + $crypto*4 + $latency}")

    echo "$recv $latency $cost"
}
