#!/usr/bin/env bash

# state: freq(Hz) volt(pu) stability

init_microgrid() {
    echo "50.0 1.00 1.0"
}

update_physical() {
    local freq=$1 volt=$2 stab=$3 recv=$4 entropy=$5 latency=$6

    # Packet loss
    if [[ "$recv" -eq 0 ]]; then
        freq=$(awk "BEGIN {print $freq - 0.08}")
        volt=$(awk "BEGIN {print $volt - 0.02}")
        stab=$(awk "BEGIN {print $stab - 0.08}")
    fi

    # Wrong control actions (entropy)
    if (( $(awk "BEGIN {print ($entropy > 0.6)}") )); then
        freq=$(awk "BEGIN {print $freq - 0.04}")
        stab=$(awk "BEGIN {print $stab - 0.05}")
    fi

    # Delayed control (latency)
    if (( $(awk "BEGIN {print ($latency > 2)}") )); then
        volt=$(awk "BEGIN {print $volt - 0.015}")
        stab=$(awk "BEGIN {print $stab - 0.05}")
    fi

    # Clamp
    stab=$(awk "BEGIN {print ($stab < 0 ? 0 : ($stab > 1 ? 1 : $stab))}")

    echo "$freq $volt $stab"
}
