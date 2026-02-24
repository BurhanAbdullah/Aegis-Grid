# Tag Notes — Aegis-Grid

## Tag Annotation Status

All 15 tags are annotated locally. One tag (`2026.1`) is protected on GitHub
and cannot be force-updated — this is correct and expected for a published release.

| Tag | Type | Status |
|-----|------|--------|
| `v1.0.0` | annotated | ✅ pushed |
| `v2.0` | annotated | ✅ pushed |
| `v3.0-agentic` | annotated | ✅ pushed (force-updated) |
| `v3.0-locked` | annotated | ✅ pushed (force-updated) |
| `v3.0-final` | annotated | ✅ pushed (force-updated) |
| `v3.3-experimental` | annotated | ✅ pushed |
| `v4.0-cyberphysical` | annotated | ✅ pushed |
| `v4.0-cyberphysical-fixed` | annotated | ✅ pushed (force-updated) |
| `v5-concept` | annotated | ✅ pushed |
| `paper-2026-final` | annotated | ✅ pushed (force-updated) |
| `paper-2026-final-with-banner` | annotated | ✅ pushed (force-updated) |
| `v2-real-grid-stable` | annotated | ✅ pushed (force-updated) |
| `v3-ledger-init` | annotated | ✅ pushed |
| `v3-ledger-semantics-locked` | annotated | ✅ pushed |
| `2026.1` | annotated | ✅ local only — **GitHub protected release tag** |

## Why 2026.1 Cannot Be Force-Pushed

`2026.1` corresponds to the GitHub Release "Aegis-Grid Research Package 2026.1"
published on Jan 25, 2026. GitHub automatically protects release tags from
being overwritten to preserve citation integrity.

**This is the correct and desired behaviour.**

The tag is annotated locally. If the annotation needs to appear on GitHub,
the release must be deleted and recreated — which would break existing citations.
**Do not do this.**

## Tags With Partial File Sets (Historical, Not Fixable)

These tags were created at commits that predate certain files. This is expected.

| Tag | Missing at tag time | Reason |
|-----|--------------------|----|
| `paper-2026-final` | `main.py`, `generate_plots.py` | Paper branch diverged before these were added |
| `paper-2026-final-with-banner` | `README.md`, `generate_plots.py` | Banner-only commit on paper branch |
| `v3-ledger-semantics-locked` | `README.md`, `main.py` | Ledger branch at semantic-lock point |
| `v3-ledger-init` | `generate_plots.py` | Init state before plot scripts added |

## Tags on Detached History

| Tag | Branch of origin | Note |
|-----|-----------------|------|
| `2026.1` | Merged via PR #4 from `paper-2026-assets` | Valid, intentional |
| `v3.3-experimental` | `origin/release/v3.3-experimental` | Valid, reachable remotely |

All tags point to valid, reachable commits. All key versioned tags contain
README.md, requirements.txt, main.py, generate_plots.py, and verify_model.py.
