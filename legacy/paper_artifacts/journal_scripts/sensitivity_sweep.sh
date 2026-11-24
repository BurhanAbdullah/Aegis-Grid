#!/bin/bash

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$BASE_DIR/journal_data/sensitivity_sweep.csv"

mkdir -p "$BASE_DIR/journal_data"

echo "packet_loss,N,mean_success" > "$OUT"

for N in 5 10 20 30 40; do
  for loss in $(seq 0 0.02 0.5); do

    result=$(python3 - <<END
import random
import numpy as np

loss = $loss
N = $N
trials = 1000

success = 0
for _ in range(trials):
    received = sum([1 for _ in range(N) if random.random() > loss])
    if received == N:
        success += 1

print(success/trials)
END
)

    echo "$loss,$N,$result" >> "$OUT"
  done
done

echo "Generated: $OUT"
