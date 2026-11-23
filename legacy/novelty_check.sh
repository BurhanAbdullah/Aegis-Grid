#!/usr/bin/env bash

ROOT="${1:-.}"

declare -A PATTERNS

PATTERNS[attack_pressure]="pressure|cap|attack_pressure|cumulative"
PATTERNS[entropy_control]="entropy|shannon|randomness|entropy_loss"
PATTERNS[adaptive_threshold]="adaptive|dynamic|threshold|reconfigure"
PATTERNS[fail_secure]="fail_secure|lockdown|irreversible|halt"
PATTERNS[agent_autonomy]="agent|autonomous|self|adaptive_agent"

echo
echo "=== AEGIS-GRID NOVELTY SIGNAL CHECK (BASH) ==="
echo "Scanning: $ROOT"
echo

for category in "${!PATTERNS[@]}"; do
    echo "[$category]"
    grep -RInE --color=never "${PATTERNS[$category]}" \
        --include="*.py" \
        --include="*.txt" \
        "$ROOT" 2>/dev/null | \
        awk -F: '{print "  - " $1}' | sort -u

    if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
        echo "  (no matches)"
    fi
    echo
done
