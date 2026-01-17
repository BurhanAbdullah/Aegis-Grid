#!/bin/bash
# 1. Force Clean-Up
find . -name "__pycache__" -type d -exec rm -rf {} +
echo "✅ Environment Purged"

# 2. Audit V1: Adaptive Resilience (Classical)
echo "-----------------------------------------------"
echo "🔍 AUDITING V1: ADAPTIVE COMMUNICATION ARCHITECTURE"
echo "-----------------------------------------------"
python3 -m tests.verify_v1

# 3. Audit V2: Post-Quantum & Time-Bounded (Isolated)
echo ""
echo "-----------------------------------------------"
echo "🛡️ AUDITING V2.0: PQ-RESILIENT & TIME-BOUNDED"
echo "-----------------------------------------------"
export PYTHONPATH=$PYTHONPATH:.
python3 v2_model/tests/audit_v2.py
