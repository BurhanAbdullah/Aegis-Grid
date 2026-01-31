#!/usr/bin/env bash

DATE=$(date +%F)
OUTDIR="audit/llm"
OUTFILE="${OUTDIR}/LLM_STATE_REPORT_${DATE}.txt"

mkdir -p "$OUTDIR"

{
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Aegis-Grid LLM Audit Report"
echo "Date: ${DATE}"
echo "Role: Post-hoc Research Auditor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

for f in README.md REPO_STRUCTURE.txt AUDIT_REPO_INVENTORY.txt SECURITY.md VERSION docs/MODEL_COMPARISON.md
do
  if [ -f "$f" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "FILE: $f"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    sed 's/^/│ /' "$f"
    echo
  else
    echo "⚠️  MISSING FILE: $f"
    echo
  fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "END OF ARTIFACT BUNDLE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "LLM INSTRUCTIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'INNER'
You are acting as a research auditor.

Read the provided repository artifacts.

Do NOT:
– suggest improvements
– optimize designs
– invent intent
– act as a controller

Only report:
– what the system claims
– what the artifacts show
– whether they are consistent

Explicitly flag:
– assumption drift
– undocumented behavior
– scope violations
– ambiguity

Respond in structured prose.
INNER
} > "$OUTFILE"

echo "Wrote: $OUTFILE"
