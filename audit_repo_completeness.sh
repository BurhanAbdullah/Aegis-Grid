#!/bin/bash
set -e

BASE="paper_results/2026"
FAIL=0

echo "========================================="
echo " AEGIS-GRID REPO COMPLETENESS AUDIT"
echo "========================================="
echo

check_file() {
  if [ ! -f "$1" ]; then
    echo "❌ MISSING: $1"
    FAIL=1
  else
    echo "✅ FOUND:  $1"
  fi
}

echo "== ROOT FILES =="
check_file "README.md"
check_file "LICENSE"
check_file "SECURITY.md"
check_file "ARTIFACT_ENTRYPOINT.md"

if grep -qi "## Citation" README.md; then
  echo "✅ README has CITATION section"
else
  echo "❌ README missing CITATION section"
  FAIL=1
fi

echo
echo "== PAPER RESULTS MODELS =="

for d in "$BASE"/*; do
  [ -d "$d" ] || continue
  MODEL=$(basename "$d")

  echo
  echo "Model: $MODEL"
  echo "---------------------"

  ls "$d"/*.csv >/dev/null 2>&1 && echo "✅ CSV present" || echo "❌ No CSV"
  ls "$d"/*.png >/dev/null 2>&1 && echo "✅ PNG present" || echo "❌ No PNG"
  [ -f "$d/README.md" ] && echo "✅ Documentation present" || echo "❌ No documentation"
  [ -f "$d/REPRODUCIBILITY.txt" ] && echo "✅ Reproducibility file present" || echo "❌ No reproducibility file"

done

echo
if [ "$FAIL" -eq 0 ]; then
  echo "========================================="
  echo "✅ REPO IS PAPER-GRADE COMPLETE"
  echo "========================================="
else
  echo "========================================="
  echo "⚠️ REPO HAS MISSING OR WEAK DOCUMENTATION"
  echo "========================================="
fi
