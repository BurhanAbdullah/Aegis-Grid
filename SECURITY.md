# Security policy

## Scope

Aegis-Grid is a research artefact. It accompanies a manuscript and exists to
make the reported measurements reproducible. It has not been hardened, audited
or certified, and it must not be deployed on a real control network.

## Supported versions

| Version | Status |
|---|---|
| 6.0 (`main`, tag `v6.0-revision`) | Maintained for the revised manuscript |
| v1–v5 (`legacy/`, earlier tags) | Archived, not maintained; their security claims were audited and in part withdrawn (see below) |

## What the code relies on

- Post-quantum and classical primitives come from the `cryptography` package
  (pinned in `requirements.txt`); nothing cryptographic is implemented from
  scratch. A vulnerability in a primitive should be reported to that project.
- The security properties claimed, and the assumptions behind them, are stated
  in [`docs/threat_model.md`](docs/threat_model.md) and
  [`docs/security_assumptions.md`](docs/security_assumptions.md).
- Claims of the earlier versions that did not hold are listed in
  [`docs/research_integrity/CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md`](docs/research_integrity/CLAIM_IMPLEMENTATION_EVIDENCE_MATRIX.md),
  and open defects, including negative results, in
  [`docs/research_integrity/KNOWN_FAILURES.md`](docs/research_integrity/KNOWN_FAILURES.md).

## Reporting a problem

Open a GitHub issue for a flaw in the protocol, the threat model, an
implementation defect or an error that affects a reported result. Include the
commit, the affected file or experiment, and the steps to reproduce it. There is
no bug bounty and no response-time commitment; confirmed problems are recorded
in `KNOWN_FAILURES.md` and fixed in the code or the documentation.
