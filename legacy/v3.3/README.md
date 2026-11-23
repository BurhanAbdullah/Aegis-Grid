# v3.3 — Extended Cyber-Physical Timing

**Research Question:** Does security logic remain coherent when physical time becomes the dominant constraint?

## Scope

This stage tightens the coupling between communication and physical timing constraints.
Messages are evaluated not only by their content but by their **arrival time relative to physical deadlines**.

## Key Design Choice

- Late information is **not degraded or flagged** — it is **invalidated entirely**
- This is a deliberate extension of the fail-secure stance from v1
- Timing is treated as a first-class security property, not a network quality metric

## Relationship to Other Versions

- Extends v3 (agent-based autonomous security) with strict physical deadline enforcement
- Feeds into v4 (grid-aware security constraints) where physical state drives policy

## Status

Conceptual + partially executable. See `simulation/` for timing constraint models.

## Parameters (version-scoped)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Deadline window | Configurable (ms) | Set per grid segment |
| Invalidation policy | Hard drop | No retry or buffering |
| Timing source | System clock (NTP-synced) | GPS-backed in v4 |

