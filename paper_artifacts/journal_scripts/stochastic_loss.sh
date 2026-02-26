#!/bin/bash

BASE_DIR="/workspaces/Aegis-Grid/paper_artifacts"
OUT="$BASE_DIR/journal_data/stochastic_loss.csv"

mkdir -p "$BASE_DIR/journal_data"

echo "state_transition_prob,N,success_rate" > "$OUT"

for p in 0.1 0.2 0.3 0.4; do
python3 <<END >> "$OUT"
import random

p = $p
N = 20
trials = 2000
success = 0

for _ in range(trials):
    state = 1
    received = 0

    for _ in range(N):
        if random.random() < p:
            state = 0
        else:
            state = 1

        if state == 1:
            received += 1

    if received == N:
        success += 1

print(f"{p},{N},{success/trials}")
END
done

echo "Generated: $OUT"
