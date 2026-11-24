#!/bin/bash

BASE="paper_artifacts/journal_data"

echo "====================================================="
echo "1. MONTE CARLO CONFIDENCE INTERVALS"
echo "====================================================="
cat $BASE/monte_carlo_ci.csv 2>/dev/null || echo "Not found"

echo ""
echo "====================================================="
echo "2. STOCHASTIC LOSS MODEL"
echo "====================================================="
cat $BASE/stochastic_loss.csv 2>/dev/null || echo "Not found"

echo ""
echo "====================================================="
echo "3. SENSITIVITY SWEEP"
echo "====================================================="
cat $BASE/sensitivity_sweep.csv 2>/dev/null || echo "Not found"

echo ""
echo "====================================================="
echo "4. ONION BASELINE LATENCY"
echo "====================================================="
cat $BASE/onion_latency.csv 2>/dev/null || echo "Not found"

echo ""
echo "====================================================="
echo "5. RECONSTRUCTION (CORE)"
echo "====================================================="
cat paper_results/2026/csv/v2_reconstruction.csv

echo ""
echo "====================================================="
echo "6. INFORMATION LEAKAGE"
echo "====================================================="
cat paper_results/2026/csv/v3_information_leakage.csv

echo ""
echo "====================================================="
echo "7. TRAFFIC ENTROPY"
echo "====================================================="
cat paper_results/2026/csv/v3_traffic_entropy.csv

echo ""
echo "====================================================="
echo "8. LATENCY COMPARISON"
echo "====================================================="
cat paper_results/2026/csv/v3_latency_comparison.csv

echo ""
echo "====================================================="
echo "9. AGENT ADAPTATION"
echo "====================================================="
cat paper_results/2026/csv/v3_agent_adaptation.csv

echo ""
echo "====================================================="
echo "10. CONTROL SAFETY"
echo "====================================================="
cat paper_results/2026/csv/v4_control_safety.csv

echo ""
echo "====================================================="
echo "11. SYSTEM COMPARISON"
echo "====================================================="
cat paper_results/2026/csv/baseline_comparison.csv

echo ""
echo "====================================================="
echo "12. LATENCY FEASIBILITY"
echo "====================================================="
cat paper_results/2026/csv/v1_latency_feasibility.csv

echo ""
echo "====================================================="
echo "END OF JOURNAL DATA DUMP"
echo "====================================================="
