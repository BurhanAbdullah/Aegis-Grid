# Tag Notes — Aegis-Grid

## Tags with Partial File Sets

Some tags were created at commits that predate certain files being added to the repo.
This is expected and does not indicate corruption.

| Tag | Missing at tag time | Reason |
|-----|--------------------|----|
| `paper-2026-final` | `main.py`, `generate_plots.py` | Paper branch diverged before these were added |
| `paper-2026-final-with-banner` | `README.md`, `generate_plots.py` | Banner-only commit on paper branch |
| `v3-ledger-semantics-locked` | `README.md`, `main.py` | Ledger branch at semantic-lock point |
| `v3-ledger-init` | `generate_plots.py` | Init state before plot scripts |

## Tags on Detached History

These tags point to commits on branches that diverged from main:

| Tag | Branch of origin |
|-----|-----------------|
| `2026.1` | `paper-2026-assets` (merged via PR #4) |
| `v3.3-experimental` | Experimental branch (now archived) |

These are valid and intentional. Check out the tag directly with:
```bash
git checkout <tag-name>
```

## All Tags Are Valid

All 15 tags point to valid, reachable commits.
All key tags (v1.0.0, v2.0, v3.x, v4.x, v5-concept) contain:
- README.md ✅
- requirements.txt ✅
- main.py ✅
- generate_plots.py ✅
- verify_model.py ✅
