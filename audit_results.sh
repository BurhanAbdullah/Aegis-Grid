#!/bin/bash
echo -e "\nSYSTEM\t\t| BASELINE\t| MEASURED\t| STATUS"
echo "-------------------------------------------------------"

# Theoretical Baselines from your provided image
declare -A BASE=( ["AegisGrid"]=0.9 ["EncryptedOnly"]=0.6 ["IEC62351"]=0.4 ["IDSAdaptive"]=0.5 )

for m in "${!BASE[@]}"; do
    # Pulling the latest score from your generated report
    val=$(grep -A 1 "System: $m" validation_report.txt | grep "Latency Score" | awk '{print $NF}')
    
    # Check if Measured > Baseline using Python for the float math
    status=$(python3 -c "print('REAL-WORLD BETTER') if $val > ${BASE[$m]} else print('UNDER-PERFORMING')")
    
    printf "%-15s | %-10s | %-10s | %s\n" "$m" "${BASE[$m]}" "$val" "$status"
done
