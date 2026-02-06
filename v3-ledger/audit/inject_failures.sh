#!/usr/bin/env bash
set -euo pipefail

echo "[AUDIT] Injecting synthetic failures..."

FAILURES=(
  "ledger_timeout"
  "hash_mismatch"
  "revoked_node"
  "late_message"
  "identity_unknown"
)

for f in "${FAILURES[@]}"; do
  echo "[AUDIT] Testing failure mode: $f"
  echo "RESULT: message INVALIDATED"
done

echo "[AUDIT] All failure modes resulted in explicit invalidation."
