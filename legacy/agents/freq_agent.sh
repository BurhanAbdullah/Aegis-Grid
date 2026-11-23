#!/usr/bin/env bash
LINE="$1"

FREQ=$(echo "$LINE" | awk -F',' '{print $NF}')

if (( $(echo "$FREQ < 49.7" | bc -l) )); then
  echo "isolate_bus_17"
elif (( $(echo "$FREQ < 49.9" | bc -l) )); then
  echo "monitor_only_bus_17"
else
  echo "no_action"
fi
