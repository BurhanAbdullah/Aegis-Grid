#!/usr/bin/env bash
set -u

echo "=== AEGIS-GRID VERSION COMPLETENESS AUDIT ==="
echo

FAIL=0
VERSIONS=(v1 v2 v3 v4 v5)

for V in "${VERSIONS[@]}"; do
  echo "------------------------------------------"
  echo "Inspecting $V"
  echo "------------------------------------------"

  if [[ ! -d "$V" ]]; then
    echo "❌ $V directory missing"
    FAIL=1
    continue
  fi

  [[ -f "$V/README.md" ]] && echo "✔ README present" || { echo "❌ README missing"; FAIL=1; }

  CODE_COUNT=$(find "$V" -type f \( -name "*.py" -o -name "*.sh" \) 2>/dev/null | wc -l | tr -d ' ')
  [[ "$CODE_COUNT" -gt 0 ]] && echo "✔ Code files: $CODE_COUNT" || echo "⚠ No code files"

  FILE_COUNT=$(find "$V" -type f | wc -l | tr -d ' ')
  [[ "$FILE_COUNT" -gt 1 ]] && echo "✔ Non-empty ($FILE_COUNT files)" || { echo "❌ Empty version"; FAIL=1; }

  echo
done

echo "------------------------------------------"
if [[ "$FAIL" -eq 0 ]]; then
  echo "✅ AUDIT PASSED"
else
  echo "⚠ AUDIT COMPLETED WITH WARNINGS"
fi
