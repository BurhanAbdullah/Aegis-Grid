#!/usr/bin/env bash

agent_decide() {
    local loss=$1 entropy=$2 freq=$3 volt=$4 stab=$5
    if (( $(awk "BEGIN {print ($stab < 0.25 || $freq < 48.8 || $volt < 0.93)}") )); then
        echo "FAIL_SECURE 2"
    elif (( $(awk "BEGIN {print ($entropy > 0.65 || $loss > 0.25)}") )); then
        echo "MITIGATE 1"
    else
        echo "NORMAL 0"
    fi
}

baseline_decide() {
    echo "NORMAL 0"
}
