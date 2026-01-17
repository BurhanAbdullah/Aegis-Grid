#!/bin/bash
set -e

echo "=============================================="
echo " AEGIS-GRID v1.0 — MODEL STRUCTURE VERIFICATION "
echo "=============================================="

fail () { echo "[FAIL] $1"; exit 1; }
pass () { echo "[ OK ] $1"; }

# 1. Check Required Directory Structure
REQ_DIRS=(core/crypto agents protocol simulation plots comparison/plots tests docs)
for dir in "${REQ_DIRS[@]}"; do
    [ -d "$dir" ] || fail "Directory $dir is missing"
    pass "Directory $dir exists"
done

# 2. Check Core Cryptographic Modules
[ -f "core/crypto/ca.py" ] || fail "CA module missing"
[ -f "core/crypto/entropy.py" ] || fail "Entropy module missing"
pass "Core crypto modules present"

# 3. Check Protocol and Agent Logic
[ -f "agents/secure_agent.py" ] || fail "Secure Agent missing"
[ -f "protocol/secure_send.py" ] || fail "Secure Send protocol missing"
pass "Agent and Protocol modules present"

echo "=============================================="
echo " RESULT: ARCHITECTURE VERIFIED "
echo "=============================================="
