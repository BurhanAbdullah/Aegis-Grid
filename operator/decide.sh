#!/usr/bin/env bash
LINE=$(tail -n 1 operator/queue.log)
ACTION=$(echo "$LINE" | awk -F'|' '{print $2}')

echo "Approve action '$ACTION'? (yes/no)"
read DECISION

if [ "$DECISION" = "yes" ]; then
  echo "$(date -u +%s)|$ACTION|APPROVED" >> operator/decisions.log
  echo "APPROVED"
else
  echo "$(date -u +%s)|$ACTION|REJECTED" >> operator/decisions.log
  echo "REJECTED"
fi
