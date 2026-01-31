# Aegis-Grid — v2-real-grid-stable

This tag represents the **stable, grid-bound realization of Version 2**
of the Aegis-Grid research framework.

---

## What this tag contains

This snapshot implements **cyber-physical enforcement bound to real grid semantics**:

- Multi-PMU cross-validation
- ROCOF-based disturbance detection
- Islanding detection logic
- AGC / control-command validation
- Seven-layer fail-secure decision pipeline
- Pressure feedback constrained by physical safety

All decisions are **fail-secure**: messages that violate timing,
physics, or authorization constraints are explicitly rejected.

---

## What this tag is

- A **frozen, executable research artifact**
- Intended for **inspection, audit, and reproduction**
- Bound to commit: `c292cf1`
- Tagged as: `v2-real-grid-stable`

---

## What this tag is not

- Not a deployment-ready system
- Not a full-paper snapshot
- Not an evolving development branch

---

## Relationship to `main`

The `main` branch documents the **entire research program**, including
all versions, assumptions, and methodology.

This tag isolates **one exact research state** for reproducibility.

For full context, see:
https://github.com/BurhanAbdullah/Aegis-Grid

---

© 2026 Burhan Abdullah — MIT License
