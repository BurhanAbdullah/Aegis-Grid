#!/bin/bash

echo "====================================================="
echo "1. Reconstruction vs Packet Loss"
echo "====================================================="
cat paper_results/2026/csv/v2_reconstruction.csv
echo

echo "====================================================="
echo "2. Information Leakage"
echo "====================================================="
cat paper_results/2026/csv/v3_information_leakage.csv
echo

echo "====================================================="
echo "3. Traffic Entropy"
echo "====================================================="
cat paper_results/2026/csv/v3_traffic_entropy.csv
echo

echo "====================================================="
echo "4. Latency Comparison"
echo "====================================================="
cat paper_results/2026/csv/v3_latency_comparison.csv
echo

echo "====================================================="
echo "5. Agent Adaptation"
echo "====================================================="
cat paper_results/2026/csv/v3_agent_adaptation.csv
echo

echo "====================================================="
echo "6. Control Safety"
echo "====================================================="
cat paper_results/2026/csv/v4_control_safety.csv
echo

echo "====================================================="
echo "7. System Comparison (incl. Onion if present)"
echo "====================================================="
cat paper_results/2026/csv/baseline_comparison.csv
echo

echo "====================================================="
echo "8. Latency Feasibility (v1)"
echo "====================================================="
cat paper_results/2026/csv/v1_latency_feasibility.csv
echo

echo "====================================================="
echo "9. Listing Additional CSV Files (if any)"
echo "====================================================="
find paper_results -name "*.csv"
echo

echo "====================================================="
echo "10. Metrics Directory (if exists)"
echo "====================================================="
ls metrics 2>/dev/null
echo

echo "====================================================="
echo "11. Simulation Directory (potential bandwidth data)"
echo "====================================================="
ls simulation 2>/dev/null
echo

echo "====================================================="
echo "12. Real Grid Directory"
echo "====================================================="
ls real_grid 2>/dev/null
echo

