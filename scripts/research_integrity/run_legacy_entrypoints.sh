#!/usr/bin/env bash
# EXP-000: execute the legacy (pre-remediation) entry points exactly as found
# on main@65f83bf and record stdout/stderr and the true exit status of each.
# Nothing is modified; failures are recorded, not fixed, by this script.
set -u
cd "$(dirname "$0")/../.."
OUT=results/raw/EXP-000_legacy_entrypoints
mkdir -p "$OUT"
SUMMARY="$OUT/summary.tsv"
printf "command\texit_status\n" > "$SUMMARY"
run() {
  local name="$1"; shift
  timeout 300 "$@" > "$OUT/$name.log" 2>&1
  local rc=$?
  printf "%s\t%s\n" "$*" "$rc" >> "$SUMMARY"
}
run main                 python3 main.py
run tests_verify_v1      python3 -m tests.verify_v1
run tests_verify_v2      python3 -m tests.verify_v2
run tests_verify_final   python3 -m tests.verify_final
run verify_model         python3 verify_model.py
run generate_validation  python3 generate_validation.py
run pytest_tests         python3 -m pytest -q tests
run agent_layer_key      python3 -c "import os;from agents.secure_agent import SecureAgent;print(SecureAgent(os.urandom(32)).get_layer_key(1).hex())"
{
  echo "git_commit=$(git rev-parse HEAD)"
  echo "python=$(python3 --version 2>&1)"
  echo "platform=$(python3 -c 'import platform;print(platform.platform())')"
  echo "pycryptodome=$(python3 -c 'import Crypto;print(Crypto.__version__)' 2>&1)"
  echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$OUT/environment.txt"
cat "$SUMMARY"
