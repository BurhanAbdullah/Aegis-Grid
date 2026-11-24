#!/usr/bin/env bash
set -euo pipefail

MODEL="gpt-4.1"
DATE="$(date +%Y-%m-%d)"
REPORT="audit/llm/LLM_STATE_REPORT_$DATE.txt"

if [[ ! -f "$REPORT" ]]; then
  echo "Audit report not found: $REPORT" >&2
  exit 1
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is not set" >&2
  exit 1
fi

echo "▶ Submitting audit report to LLM..." >&2

PAYLOAD=$(jq -n \
  --arg model "$MODEL" \
  --arg content "$(cat "$REPORT")" \
  '{
    model: $model,
    temperature: 0,
    messages: [
      {role: "system", content: "You are a research auditor. Do not suggest improvements."},
      {role: "user", content: $content}
    ]
  }')

RESPONSE=$(curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer '"$OPENAI_API_KEY"'" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "" >> "$REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$REPORT"
echo "LLM AUDIT RESPONSE" >> "$REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$REPORT"
echo "" >> "$REPORT"

echo "$RESPONSE" | jq -r '.choices[0].message.content' >> "$REPORT"

echo "✔ LLM response appended to $REPORT"
