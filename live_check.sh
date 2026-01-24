#!/bin/bash
echo "======================================================="
echo "       LIVE ARCHITECTURAL INTEGRITY CHECK              "
echo "======================================================="

# 1. Performance Measurement
start=$(date +%s%N)
for i in {1..1000}; do
    python3 -c "from core.crypto.entropy import verify_indistinguishable; verify_indistinguishable(1024, 1024)"
done
end=$(date +%s%N)
runtime=$(( (end - start) / 1000000 ))

# 2. Logic Verification (Does it actually work?)
valid=$(python3 -c "from core.crypto.entropy import verify_indistinguishable; print(verify_indistinguishable(1024, 1024))")
invalid=$(python3 -c "from core.crypto.entropy import verify_indistinguishable; print(verify_indistinguishable(1024, 1025))")

echo "Execution Time (1000 cycles): $runtime ms"
echo "Valid Packet Result: $valid"
echo "Invalid Packet Result: $invalid"

if [[ "$valid" == "True" && "$invalid" == "False" ]]; then
    echo "STATUS: LOGIC OPERATIONAL"
else
    echo "STATUS: LOGIC FAILURE"
fi
