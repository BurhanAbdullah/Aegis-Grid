#!/usr/bin/env bash
LINE="$1"

# Replace frequency with malicious low value
IFS=',' read -ra F <<< "$LINE"
F[-1]="49.2"

echo "$(IFS=,; echo "${F[*]}")"
