#!/usr/bin/env bash
set -euo pipefail

echo "[INIT] resetting state"

mkdir -p metrics ledger/state
: > ledger/chain.log
: > ledger/state/reputation.log
: > metrics/metrics.log

echo "0|$(date -u +%s)|system|init|0|0" >> ledger/chain.log

STEP=0

for LINE in $(ls real_grid/pmu_data/ieee14/*.csv); do
  tail -n +2 "$LINE" | while read -r ROW; do
    STEP=$((STEP+1))
    TS=$(date -u +%s)

    echo "[STEP $STEP] observation"

    consensus/collect_votes.sh "$ROW" >/dev/null
    VERDICT=$(consensus/decide.sh)

    echo "$TS|step=$STEP|verdict=$VERDICT" >> metrics/metrics.log
    sleep 1
  done
done

echo
echo "[DONE] experiment complete"
echo
echo "Final reputation:"
cat ledger/state/reputation.log || true
