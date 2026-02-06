#!/usr/bin/env bash
set -euo pipefail

echo "[Aegis-Grid] Initializing V3-Ledger research track..."

BASE_DIR="v3-ledger"
DATE_TAG=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ -d "$BASE_DIR" ]; then
  echo "ERROR: $BASE_DIR already exists. Aborting to preserve immutability."
  exit 1
fi

mkdir -p "$BASE_DIR"/{core,ledger,identity,audit,docs,scripts,tags}

# -----------------------------
# Core invariants
# -----------------------------
cat <<EOF > "$BASE_DIR/RESEARCH_SCOPE.md"
# Aegis-Grid V3-Ledger

Status: ACTIVE (Research Track)
Initialized: $DATE_TAG

Scope:
- Hybrid off-chain communication with on-chain verification
- Blockchain used ONLY for identity, commitments, and revocation
- No payloads, messages, or control data on-chain

Non-Goals:
- Performance optimisation
- Deployment readiness
- Public blockchain dependency

This track exists to answer one question:

Can fail-secure, agent-based communication gain *audit-grade integrity*
without sacrificing real-time safety?
EOF

# -----------------------------
# Ledger assumptions
# -----------------------------
cat <<EOF > "$BASE_DIR/ledger/ASSUMPTIONS.md"
Ledger Assumptions:

1. Permissioned consensus (PoA or equivalent)
2. Finality < physical control deadlines
3. Ledger is append-only
4. Ledger compromise is detectable, not survivable
5. Ledger failure results in explicit communication invalidation

Any violation invalidates this model.
EOF

# -----------------------------
# Identity model
# -----------------------------
cat <<EOF > "$BASE_DIR/identity/IDENTITY_MODEL.md"
Identity Model:

- Each node possesses a long-term cryptographic identity
- Public keys are registered on-ledger
- Key rotation is explicit and logged
- Revocation is immediate and irreversible
- No implicit trust or transitive trust

Identity failure = node invalidation
EOF

# -----------------------------
# Core semantics
# -----------------------------
cat <<EOF > "$BASE_DIR/core/SEMANTICS.md"
Core Semantics:

- Messages are evaluated off-chain
- Hash commitments MAY be recorded on-chain
- Verification is optional but auditable
- Ledger unavailability MUST reduce capability, not safety

Fail-secure rule:
If verification cannot complete within bounds, the message is invalid.
EOF

# -----------------------------
# Audit rules
# -----------------------------
cat <<EOF > "$BASE_DIR/audit/AUDIT_RULES.md"
Audit Rules:

- All on-chain events are reproducible
- Hashes must map to deterministic message canonicalization
- No probabilistic acceptance
- All failures are terminal and logged

Audit completeness > sys
