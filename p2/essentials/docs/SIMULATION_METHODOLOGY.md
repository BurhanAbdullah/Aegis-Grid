Simulation Methodology and Reproducibility Clarification

This document clarifies the scope, assumptions, and reproducibility properties
of the Aegis-Grid simulation results.

1. Network Topology
All simulations assume a single-hop logical communication channel between a
control entity (EMS / SCADA master) and a field device (PMU / relay).
Routing, queuing, and multi-path effects are intentionally excluded to isolate
security semantics from network engineering artifacts.

2. Traffic Model
Packet emission follows a Poisson process with fixed rate λ.
Dummy and real packets are indistinguishable by construction.

3. Simulation Runs
Simulations are deterministic given fixed parameters.
Results are generated from analytical models or single-run simulations because
the architecture enforces hard invariants rather than probabilistic outcomes.

4. Duration
Each simulation run spans a bounded time horizon sufficient to cover:
- message generation
- fragment transmission
- validity window expiration
- agent adaptation response (where applicable)

5. Statistical Variance
Statistical variance and confidence intervals are intentionally omitted.
Aegis-Grid is fail-secure by construction:
- partial reconstruction probability is identically zero
- expired messages are deterministically invalidated
- latency constraints are hard bounds

Repeated runs produce identical outcomes under identical parameters.

6. Baseline Comparisons
Comparisons against IEC 62351, encrypted-only traffic, and IDS-based security
are analytical and conceptual.
No experimental claims are made for third-party systems.

This design choice prioritizes correctness, auditability, and semantic clarity
over benchmark-driven performance claims.

Baseline System Simulation Scope

Numerical simulation results are intentionally restricted to Aegis-Grid.
Conventional systems such as IEC 62351, encrypted-only channels, and
IDS-based security do not define the architectural invariants evaluated
(time-bounded correctness, fail-secure expiration, fragment semantics).

As a result, numerical comparison would require inventing behaviors not
specified by those systems, which would be misleading.
