#!/usr/bin/env bash
LINE="$1"

for AG in A B C; do
  AGENT="agent_$AG"

  if ledger/state/is_banned.sh "$AGENT"; then
    echo "[SKIP] $AGENT banned"
    continue
  fi

  ACTION=$(./agents/freq_agent_${AG}.sh "$LINE")
  ledger/append_block.sh "$AGENT" proposal "$ACTION"
done
