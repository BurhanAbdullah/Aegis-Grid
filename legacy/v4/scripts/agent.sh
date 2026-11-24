#!/usr/bin/env bash

agent_decide() {
    local loss=$1 entropy=$2 freq=$3 volt=$4 stab=$5

    # Emergency islanding
    if (( $(awk "BEGIN {print ($stab < 0.35 || $freq < 49.2 || $volt < 0.94)}") )); then
        echo "FAIL_SECURE 2"

    # Suspicious environment
    elif (( $(awk "BEGIN {print ($entropy > 0.6 || $loss > 0.2)}") )); then
        echo "MITIGATE 1"

    else
        echo "NORMAL 0"
    fi
}
