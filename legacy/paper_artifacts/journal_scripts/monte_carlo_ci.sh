#!/bin/bash

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$BASE_DIR/journal_data/monte_carlo_ci.csv"

mkdir -p "$BASE_DIR/journal_data"

echo "packet_loss,N,mean,lower_ci,upper_ci" > "$OUT"

for N in 10 20 30; do
  for loss in $(seq 0 0.05 0.5); do

    python3 - <<END >> "$OUT"
import random, numpy as np

loss = $loss
N = $N
trials = 2000
results = []

for _ in range(trials):
    received = sum([1 for _ in range(N) if random.random() > loss])
    results.append(1 if received == N else 0)

mean = np.mean(results)
std = np.std(results)
ci = 1.96 * std / np.sqrt(trials)

print(f"{loss},{N},{mean},{mean-ci},{mean+ci}")
END

  done
done

echo "Generated: $OUT"
