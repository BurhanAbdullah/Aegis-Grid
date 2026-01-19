#!/usr/bin/env bash
# state: freq volt stab

init_grid() {
    echo "50.0 1.00 1.0"
}

update_grid() {
    local freq=$1 volt=$2 stab=$3 recv=$4 entropy=$5 latency=$6

    if [[ "$recv" -eq 0 ]]; then
        freq=$(awk "BEGIN {print $freq - 0.08}")
        volt=$(awk "BEGIN {print $volt - 0.02}")
        stab=$(awk "BEGIN {print $stab - 0.08}")
    fi

    if (( $(awk "BEGIN {print ($entropy > 0.6)}") )); then
        freq=$(awk "BEGIN {print $freq - 0.04}")
        stab=$(awk "BEGIN {print $stab - 0.05}")
    fi

    if (( $(awk "BEGIN {print ($latency > 2)}") )); then
        freq=$(awk "BEGIN {print $freq - 0.03}")
        stab=$(awk "BEGIN {print $stab - 0.03}")
    fi

    stab=$(awk "BEGIN {print ($stab < 0 ? 0 : $stab)}")
    echo "$freq $volt $stab"
}
