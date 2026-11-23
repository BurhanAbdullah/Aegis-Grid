# comparison/

Analytical model comparison against reference architectures.

## Purpose

Provides a **model-level qualitative and analytical comparison** of Aegis-Grid
against existing approaches (Mixnets and similar privacy-preserving overlays).

## Important Scope Clarification

This is **not** an empirical benchmark against production deployments.

Comparisons are:
- Based on declared architectural properties
- Derived from analytical models, not live systems
- Focused on failure semantics, threat models, and decision boundaries

No claims of superior throughput, latency, or scalability are made.

## What Is Compared

| Dimension | Aegis-Grid | Reference |
|-----------|-----------|-----------|
| Failure model | Explicit invalidation | Graceful degradation |
| Physical safety coupling | First-class | Absent or optional |
| Availability trade-off | Sacrificed for safety | Preserved |
| Timing semantics | Hard deadlines | Best-effort |

## Contents

Model-generated figures and analytical derivations.
See `generate_plots.py` for figure generation.
