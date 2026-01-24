#!/bin/bash
echo -e "System\t\t| Baseline | Measured | Status"
echo -e "-------------------------------------------------------"

# Extracting from your validation_report.txt
declare -A BASELINES=( ["AegisGrid"]=0.9 ["EncryptedOnly"]=0.6 ["IEC62351"]=0.4 ["IDSAdaptive"]=0.5 )

for m in "${!BASELINES[@]}"; do
    measured=$(grep -A 1 "System: $m" validation_report.txt | grep "Latency Score" | awk '{print $NF}')
    base=${BASELINES[$m]}
    
    # Check if measured is higher than baseline
    status=$(python3 -c "print('BETTER') if $measured > $base else print('SUBSPACE')")
    printf "%-15s\t| %-8s | %-8s | %s\n" "$m" "$base" "$measured" "$status"
done
