#!/bin/bash
set -e

BASE="paper_results/2026/v5-concept"

echo "Enforcing paper whitelist for v5-concept..."

find "$BASE" -mindepth 1 -type d \
  ! -name "." \
  ! -path "$BASE" \
  -exec rm -rf {} +

find "$BASE" -type f \
  ! -name "sensitivity_matrix.csv" \
  ! -name "sensitivity_matrix_elastic.csv" \
  ! -name "counts.csv" \
  ! -name "REPRODUCIBILITY.txt" \
  ! -name "fig*.png" \
  ! -name "frequency.png" \
  ! -name "stability.png" \
  ! -name "voltage.png" \
  -delete

find "$BASE" -type f -exec sha256sum {} \; > "$BASE/REPRODUCIBILITY.txt"

echo "v5-concept is now paper-clean"
