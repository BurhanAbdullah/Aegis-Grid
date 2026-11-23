#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# Aegis-Grid v4.0 Cyber-Physical Simulation (SAFE VERSION)
# ============================================================

# ---- Single execution guard ----
if [[ "${AEGIS_V4_RUNNING:-0}" == "1" ]]; then
  exit 0
fi
export AEGIS_V4_RUNNING=1

echo "[v4.0] Starting cyber-physical simulation"

# ---- Dependency check (bc is OPTIONAL) ----
if command -v bc >/dev/null 2>&1; then
  USE_BC=1
else
  USE_BC=0
  echo "[WARN] 'bc' not found. Using integer-only fallback."
fi
export USE_BC

# ---- Output directory ----
OUT_DIR="output"
mkdir -p "$OUT_DIR"
OUT_FILE="$OUT_DIR/v4_cyberphysical_trace.csv"

echo "time,load,stress,response" > "$OUT_FILE"

# ---- Simple cyber-physical loop (SAFE, deterministic) ----
for t in $(seq 0 20); do
  load=$((50 + t))

  if [[ "$USE_BC" == "1" ]]; then
    stress=$(echo "$load * 0.97" | bc -l)
  else
    stress=$load
  fi

  response=$((stress > 60 ? 1 : 0))

  echo "$t,$load,$stress,$response" >> "$OUT_FILE"
done

echo "[v4.0] Simulation completed successfully"
echo "[v4.0] Output written to $OUT_FILE"
exit 0

