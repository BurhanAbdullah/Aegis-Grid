# LLM Audit Tooling

## Purpose

Scripts in `audit/llm/scripts/` perform automated consistency checks on:
- Repository structure vs. README claims
- Commit message integrity
- Version directory completeness
- Figure reproducibility metadata

## Why Reports Are Gitignored

Generated reports contain run-specific timestamps and paths that would create
noisy diffs on every CI run. They are regenerated on demand.

## How to Run

```bash
bash audit/llm/scripts/run_audit.sh 2>&1 | tee audit_output.txt
```

## Methodology

- Static analysis: directory tree vs. README claims
- Commit scan: keyword matching for obfuscation, credential leaks
- Syntax check: Python and shell scripts
- No LLM API calls are made by default — analysis is deterministic

## Interpreting Results

Each check emits: PASS / FAIL / WARN / FIX
- PASS: claim verified
- FAIL: discrepancy found (action required)
- WARN: potential issue (review recommended)  
- FIX: automatic correction applied

