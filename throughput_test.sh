#!/bin/bash
echo "Starting High-Frequency Throughput Test..."
start=$(date +%s%N)
for i in {1..5000}; do
    python3 -c "from core.crypto.entropy import verify_indistinguishable; verify_indistinguishable(1024, 1024)"
done
end=$(date +%s%N)
runtime=$(( (end - start) / 1000000 ))
echo "Total Execution Time for 5000 cycles: $runtime ms"
