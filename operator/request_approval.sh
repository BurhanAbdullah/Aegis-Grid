#!/usr/bin/env bash
ACTION="$1"
TS=$(date -u +%s)

echo "$TS|$ACTION|PENDING" >> operator/queue.log
echo "[OPERATOR] approval requested for: $ACTION"
