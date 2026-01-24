#!/bin/bash
set -e

BASE="paper_results/2026"
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
STASH_NAME="paper-model-run-$(date +%s)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

confirm_save() {
  echo
  read -p "Save these results to paper_results/2026? (y/n): " ans
  if [ "$ans" != "y" ]; then
    echo -e "${RED}DISCARDED — Not saved${NC}"
    return 1
  fi
  return 0
}

run_tag() {
  TAG="$1"
  OUT="$BASE/$TAG"

  echo
  echo "=============================================="
  echo "RUNNING MODEL FROM TAG: $TAG"
  echo "=============================================="

  echo "[SAFE] Stashing local results..."
  git stash push -u -m "$STASH_NAME" > /dev/null

  git checkout -q "$TAG"
  mkdir -p "$OUT"

  echo
  echo "=== Searching for model runners in tag ==="
  find . -maxdepth 3 -type f \( -name "*.py" -o -name "*.sh" \) | grep -E "run|model|simulate|generate|main" || true

  echo
  echo "=== Executing model (tag-native) ==="

  if [ -f "run_model.sh" ]; then
    bash run_model.sh | tee "$OUT/terminal.log"
  elif [ -f "model_runner" ]; then
    bash model_runner | tee "$OUT/terminal.log"
  elif [ -f "main.py" ]; then
    python3 main.py | tee "$OUT/terminal.log"
  else
    echo -e "${RED}No runnable model found in this tag${NC}"
  fi

  echo
  echo "=== Detected Outputs ==="
  find . -type f \( -name "*.csv" -o -name "*.png" \)

  if confirm_save; then
    echo
    echo "Saving outputs..."
    find . -type f \( -name "*.csv" -o -name "*.png" \) -exec cp --parents {} "$OUT" \;
    echo -e "${GREEN}Saved to $OUT${NC}"
  fi

  echo
  echo "[SAFE] Restoring original branch + files..."
  git checkout -q "$ORIGINAL_BRANCH"
  git stash pop > /dev/null || true
}

if [ -z "$1" ]; then
  echo "Usage:"
  echo "  ./run_tag_model.sh v3.0-locked"
  echo "  ./run_tag_model.sh v3.0-agentic"
  echo "  ./run_tag_model.sh v5-concept"
  exit 1
fi

run_tag "$1"

echo
echo -e "${GREEN}Returned to branch: $ORIGINAL_BRANCH${NC}"
