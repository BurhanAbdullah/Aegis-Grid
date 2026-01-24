#!/bin/bash
set -e

OUT="paper_results/2026/v3.0-agentic"
mkdir -p "$OUT"

echo "Saving paper-valid v3.0-agentic results..."

# CSVs (real model outputs)
for f in \
  data/processed/sensitivity_matrix.csv \
  data/processed/sensitivity_matrix_elastic.csv \
  .novelty_state/counts.csv
do
  if [ -f "$f" ]; then
    echo "Copying $f"
    cp "$f" "$OUT/"
  else
    echo "Skipping missing: $f"
  fi
done

# Figures (only real IEEE plots, no archives)
for f in plots/ieee/fig*.png
do
  if [ -f "$f" ]; then
    echo "Copying $f"
    cp "$f" "$OUT/"
  fi
done

# Reproducibility proof
find "$OUT" -type f -exec sha256sum {} \; > "$OUT/REPRODUCIBILITY.txt"

echo "Saved clean paper artifacts to $OUT"
