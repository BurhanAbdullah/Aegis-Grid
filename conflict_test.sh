#!/bin/bash
echo "Running Protocol Integrity Check..."
echo "-------------------------------------------------------"

# Valid Case: lengths match
valid=$(python3 -c "from core.crypto.entropy import verify_indistinguishable; print(verify_indistinguishable(1024, 1024))")

# Invalid Case: lengths mismatch (Attacker/Error)
invalid=$(python3 -c "from core.crypto.entropy import verify_indistinguishable; print(verify_indistinguishable(1024, 1025))")

echo "Matching Traffic: $valid"
echo "Mismatched Traffic: $invalid"

if [[ "$valid" == "True" && "$invalid" == "False" ]]; then
    echo "STATUS: LOGIC VERIFIED - Models are correctly discriminating traffic."
else
    echo "STATUS: LOGIC FAILURE - Models are not performing basic validation."
fi
