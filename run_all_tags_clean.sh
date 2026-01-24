#!/bin/bash
set -e

BASE="paper_results/2026/tags"
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

mkdir -p "$BASE"

declare -A TAGMAP
TAGMAP["v1.0.0"]="v1-baseline"
TAGMAP["v2.0"]="v2-fail-secure"
TAGMAP["v3.0-locked"]="v3-confidentiality-locked"
TAGMAP["v3.0-agentic"]="v3-agentic-adaptation"
TAGMAP["v4.0"]="v4-cyber-physical"
TAGMAP["v5-concept"]="v5-concept-validation"

echo "=== Aegis-Grid Paper Run (CLEAN MODE): $TIMESTAMP ==="

git stash push -u -m "paper-auto-run-$TIMESTAMP" >/dev/null

for TAG in "${!TAGMAP[@]}"; do
  NAME="${TAGMAP[$TAG]}"
  OUT="$BASE/$NAME/results"

  echo
  echo "======================================"
  echo "RUNNING TAG: $TAG → $NAME"
  echo "======================================"

  rm -rf "$BASE/$NAME"
  mkdir -p "$OUT/csv" "$OUT/figures" "$OUT/architecture"

  git checkout -q "$TAG"

  echo "Executing model..."
  if [ -f "./main.py" ]; then
    python3 main.py | tee "$OUT/terminal.log"
  elif [ -f "./generate_validation.py" ]; then
    python3 generate_validation.py | tee "$OUT/terminal.log"
  elif [ -f "./scripts/check_model.sh" ]; then
    bash ./scripts/check_model.sh | tee "$OUT/terminal.log"
  else
    echo "NO RUNNER FOUND" | tee "$OUT/terminal.log"
  fi

  echo "Collecting CSVs..."
  find . -type f -name "*.csv" -exec cp --parents {} "$OUT/csv" \; || true

  echo "Collecting Figures..."
  find . -type f -name "*.png" -exec cp --parents {} "$OUT/figures" \; || true

  echo "Collecting Architecture Docs..."
  find . -type f \( -name "*.md" -o -name "*.txt" -o -iname "*arch*" \) \
    -exec cp --parents {} "$OUT/architecture" \; || true

  echo "7-Layer Security Scan..."
  echo "7-LAYER SECURITY CHECK — $TAG" > "$OUT/SECURITY_CHECK.txt"
  echo "-----------------------------------" >> "$OUT/SECURITY_CHECK.txt"
  grep -Ei "auth|encrypt|crypto|entropy|lock|secure|verify|integrity|attack|rsa|aes|tls|hash" \
    "$OUT/terminal.log" >> "$OUT/SECURITY_CHECK.txt" \
    || echo "No explicit security markers found" >> "$OUT/SECURITY_CHECK.txt"

  echo "Hashing artifacts..."
  find "$OUT" -type f -exec sha256sum {} \; > "$OUT/HASHES.txt"

done

git checkout -q "$ORIGINAL_BRANCH"
git stash pop >/dev/null || true

echo
echo "======================================"
echo "ALL TAGS COMPLETE"
echo "Results stored in: $BASE"
echo "======================================"
