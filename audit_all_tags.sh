#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

OUT_CSV="tag_arch_audit.csv"
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Tag,v1_latency,v1_generator,v2_binary_rule,v2_window,v3_zero_leakage,v3_emission_rate,v4_control_logic" > "$OUT_CSV"

echo "======================================================="
echo "   AEGIS-GRID ARCHITECTURAL TAG AUDIT (v1 → v4)       "
echo "======================================================="

check() {
  local pattern="$1"
  local file="$2"

  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo "PASS"
  else
    echo "FAIL"
  fi
}

for tag in $(git tag); do
  echo
  echo "---------------------------------------------"
  echo "Testing tag: $tag"
  echo "---------------------------------------------"

  git checkout "$tag" > /dev/null 2>&1

  v1_lat=$(check "LATENCY_BOUND" core/v1/latency.py)
  v1_gen=$(check "message_sizes" core/v1/generator.py)

  v2_bin=$(check "reconstruction_result = 1 if" core/v2/reconstruct.py)
  v2_win=$(check "validity_window" core/v2/reconstruct.py)

  v3_leak=$(check "leakage_metric = 0" core/v3/confidentiality.py)
  v3_emit=$(check "packet_emission_rate" core/v3/traffic.py)

  v4_ctrl=$(check "execute" core/v4/control.py)

  printf "%s,%s,%s,%s,%s,%s,%s,%s\n" \
    "$tag" "$v1_lat" "$v1_gen" \
    "$v2_bin" "$v2_win" \
    "$v3_leak" "$v3_emit" \
    "$v4_ctrl" >> "$OUT_CSV"

  for pair in \
    "v1_latency:$v1_lat" \
    "v1_generator:$v1_gen" \
    "v2_binary_rule:$v2_bin" \
    "v2_window:$v2_win" \
    "v3_zero_leakage:$v3_leak" \
    "v3_emission_rate:$v3_emit" \
    "v4_control_logic:$v4_ctrl"
  do
    key=${pair%%:*}
    val=${pair##*:}

    if [ "$val" = "PASS" ]; then
      echo -e "  ${GREEN}[VALID]${NC} $key"
    else
      echo -e "  ${RED}[MISSING]${NC} $key"
    fi
  done
done

git checkout "$ORIGINAL_BRANCH" > /dev/null 2>&1

echo
echo "======================================================="
echo " AUDIT COMPLETE"
echo " CSV OUTPUT: $OUT_CSV"
echo "======================================================="
