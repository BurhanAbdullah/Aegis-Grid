#!/usr/bin/env bash
set -euo pipefail
trap 'echo "❌ FAILED at line $LINENO"; exit 2' ERR

echo "=========================================="
echo " AEGIS-GRID INVARIANT EXECUTION PIPELINE"
echo "=========================================="

OUT_BASE="paper_results/2026"
CSV_DIR="${OUT_BASE}/csv"
PNG_DIR="${OUT_BASE}/png"

echo "[+] Cleaning previous CSV/PNG"
rm -rf "${OUT_BASE}"
mkdir -p "${CSV_DIR}" "${PNG_DIR}"

# ---------------- v1 ----------------
echo "[v1] Time-Bounded Feasibility"
python3 verify_model.py \
  --version v1 \
  --out "${CSV_DIR}/v1_latency.csv"

# ---------------- v2 ----------------
echo "[v2] Fail-Secure Reconstruction"
python3 verify_model.py \
  --version v2 \
  --out "${CSV_DIR}/v2_reconstruction.csv"

# ---------------- v3 ----------------
echo "[v3] Zero Leakage + Indistinguishability"
python3 verify_model.py \
  --version v3 \
  --out "${CSV_DIR}/v3_security.csv"

# ---------------- v4 ----------------
echo "[v4] Fail-Secure Cyberphysical Control"
python3 verify_model.py \
  --version v4 \
  --out "${CSV_DIR}/v4_control.csv"

# ---------------- v5 (if conceptual, still validated) ----------------
if [ -d v5 ]; then
  echo "[v5] Concept / Structural Validation"
  python3 verify_model.py \
    --version v5 \
    --out "${CSV_DIR}/v5_concept.csv"
fi

# ---------------- Reproducibility ----------------
echo "[+] Reproducibility check"
python3 generate_validation.py \
  --input "${CSV_DIR}" \
  --deterministic-only

# ---------------- CSV → PNG ----------------
echo "[+] Generating plots"
python3 generate_plots.py \
  --input "${CSV_DIR}" \
  --output "${PNG_DIR}" \
  --exact \
  --no-random \
  --no-smoothing

echo "=========================================="
echo " ✅ ALL CHECKS PASSED"
echo " Results in ${OUT_BASE}"
echo "=========================================="
