#!/bin/bash

RESULT_DIR="tag_results"

if [ ! -d "$RESULT_DIR" ]; then
    echo "ERROR: $RESULT_DIR directory not found."
    exit 1
fi

echo "Tag,Model,Latency,Leakage" > tag_summary.csv

for log in "$RESULT_DIR"/*.log; do
    tag=$(basename "$log" .log)

    awk -v TAG="$tag" '
    /System:/ {model=$2}
    /Latency Score:/ {lat=$NF}
    /Leakage Risk:/ {
        leak=$NF
        printf "%s,%s,%s,%s\n", TAG, model, lat, leak
    }
    ' "$log" >> tag_summary.csv
done

echo
echo "Summary Table:"
echo "-------------------------------------------------------"
column -t -s, tag_summary.csv

echo
echo "CSV saved to: tag_summary.csv"
