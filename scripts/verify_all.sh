#!/usr/bin/env bash
# One-command verification for the v6 research artefact.
# Every stage prints PASS / FAIL / SKIPPED / NOT RUN / BLOCKED with its reason.
# Exit status is non-zero if any stage FAILs. No stage is masked.
#
#   ./scripts/verify_all.sh            # fast: env, lint, tests, mutation smoke, result integrity
#   ./scripts/verify_all.sh --smoke    # + short smoke runs of every experiment runner (~5 min)
set -u
cd "$(dirname "$0")/.."
SMOKE=0; [ "${1:-}" = "--smoke" ] && SMOKE=1
declare -a NAMES STATUS REASON
rc=0
record() { NAMES+=("$1"); STATUS+=("$2"); REASON+=("$3"); [ "$2" = "FAIL" ] && rc=1; }
run() {   # run <name> <command...>
  local n="$1"; shift
  local log; log=$(mktemp)
  if "$@" >"$log" 2>&1; then record "$n" PASS "$(tail -1 "$log" | cut -c1-90)"
  else record "$n" FAIL "$(tail -3 "$log" | tr '\n' ' ' | cut -c1-160)"; fi
  rm -f "$log"
}

# 1. environment
if python3 - <<'PY'
import ssl, sys
from importlib.metadata import version
req = {l.split("==")[0]: l.split("==")[1].strip() for l in open("requirements-remediation.txt") if "==" in l}
bad = {k: (v, version(k)) for k, v in req.items() if version(k) != v}
assert not bad, bad
assert ssl.OPENSSL_VERSION.startswith("OpenSSL 3.5"), ssl.OPENSSL_VERSION
PY
then record "environment (pinned versions)" PASS "requirements-remediation.txt matched"
else record "environment (pinned versions)" FAIL "version mismatch; see requirements-remediation.txt"; fi

# 2. byte-compile new code
run "compile aegis_pq baselines experiments" python3 -m compileall -q aegis_pq baselines experiments

# 3. tests
run "pytest (unit, integration, security)" python3 -m pytest -q -p no:cacheprovider

# 4. mutation smoke: each disabled check must make at least one test fail
mut() {   # mut <name> <file> <python-literal-old> <python-literal-new> <test-selector>
  local n="$1" f="$2" old="$3" new="$4" sel="$5"
  cp "$f" "$f.verify_bak"
  python3 - "$f" "$old" "$new" <<'PY'
import sys; p, o, n = sys.argv[1:]; s = open(p).read(); assert o in s, o; open(p, "w").write(s.replace(o, n, 1))
PY
  if python3 -m pytest -q -p no:cacheprovider -x $sel >/dev/null 2>&1; then record "mutation: $n" FAIL "tests still pass with check disabled"
  else record "mutation: $n" PASS "disabled check detected"; fi
  mv "$f.verify_bak" "$f"
}
mut "replay window" aegis_pq/channel.py "win.check(seq)" "pass" tests/security
mut "deadline check" aegis_pq/channel.py "raise Reject(Reason.DEADLINE)" "pass" tests/security
mut "AONT canary" aegis_pq/aont.py 'if x[-16:] != CANARY or' 'if False and' tests/unit/test_aont.py
mut "shaper late drop" aegis_pq/shaping.py "while self._q and self._q[0][0] < now_ms:" "while False:" tests/unit/test_shaping.py

# 5. committed results: every run directory has config, environment, status
if python3 - <<'PY'
import glob, json, os, sys
bad = []
for d in glob.glob("results/raw/EXP-0[0-9][0-9]/run_*"):
    for f in ("config.json", "environment.json", "status.json"):
        if not os.path.exists(os.path.join(d, f)): bad.append(f"{d}/{f}")
assert not bad, bad
print(len(glob.glob("results/raw/EXP-0[0-9][0-9]/run_*")), "run directories complete")
PY
then record "result provenance files" PASS "config/environment/status present"
else record "result provenance files" FAIL "missing provenance files"; fi

# 6. manuscript numbers trace to results (generated table check)
if [ -f scripts/check_manuscript_numbers.py ]; then run "manuscript numbers vs results" python3 scripts/check_manuscript_numbers.py
else record "manuscript numbers vs results" "NOT RUN" "scripts/check_manuscript_numbers.py not present"; fi

# 7. smoke runs of experiment runners
if [ $SMOKE = 1 ]; then
  export AEGIS_RESULTS_DIR="$(mktemp -d)/smoke"
  run "smoke EXP-003" python3 experiments/runners/exp003_reliability.py experiments/configs/smoke/EXP-003.json
  run "smoke EXP-007" python3 experiments/runners/exp007_cap_detection.py experiments/configs/smoke/EXP-007.json
  run "smoke EXP-009" python3 experiments/runners/exp009_protocol_baselines.py experiments/configs/smoke/EXP-009.json
  run "smoke EXP-002" python3 experiments/runners/exp002_crypto_bench.py experiments/configs/smoke/EXP-002.json
  run "smoke EXP-004" python3 experiments/runners/exp004_partial_capture.py experiments/configs/smoke/EXP-004.json
  run "smoke EXP-005" python3 experiments/runners/exp005_traffic_capture.py experiments/configs/smoke/EXP-005.json
  run "smoke EXP-006 (on smoke EXP-005)" python3 experiments/runners/exp006_traffic_attacker.py experiments/configs/smoke/EXP-006.json
  run "smoke EXP-008" python3 experiments/runners/exp008_cyberphysical_agc.py experiments/configs/smoke/EXP-008.json
  run "smoke EXP-013" python3 experiments/runners/exp013_tls_chain_matched.py experiments/configs/smoke/EXP-013.json
else
  record "experiment smoke runs" SKIPPED "pass --smoke to run (writes to a temporary directory)"
fi

# 8. hardware results
record "embedded / RTU hardware benchmarks" BLOCKED "no embedded hardware available; all timings are x86-64 VM measurements"

printf '\n%-48s %-8s %s\n' STAGE STATUS DETAIL
for i in "${!NAMES[@]}"; do printf '%-48s %-8s %s\n' "${NAMES[$i]}" "${STATUS[$i]}" "${REASON[$i]}"; done
exit $rc
