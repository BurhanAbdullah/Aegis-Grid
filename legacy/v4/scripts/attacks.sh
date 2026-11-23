#!/usr/bin/env bash

attack_loss() {
    local t=$1
    if (( t >= 45 && t <= 80 )); then
        awk "BEGIN {print 0.15 + ($t-45)*0.015}"
    else
        echo 0.05
    fi
}

attack_entropy() {
    local t=$1
    # Decoy phase
    if (( t >= 15 && t <= 30 )); then
        echo 0.75
    # Coordinated cyber-physical attack
    elif (( t >= 45 && t <= 80 )); then
        echo 0.95
    else
        echo 0.1
    fi
}
