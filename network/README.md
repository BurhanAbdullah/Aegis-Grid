# network/

Network layer simulation for Aegis-Grid.

## Purpose

Models the communication channel between grid nodes.
Implements fragmentation, reassembly, dummy traffic injection,
and loss-resilient routing used across all research versions.

## Key Behaviours

- **Fragmentation**: Messages are split and reassembled under the fail-secure rules of v1
- **Dummy traffic**: Injected to maintain statistical indistinguishability (KL ≈ 0 target)
- **Loss resilience**: Packet loss is modelled; no retransmit — lost = invalid

## Relationship to Versions

| Version | Network behaviour |
|---------|------------------|
| v1 | Baseline fragmentation + strict reassembly |
| v2 | Adaptive threshold under sustained channel pressure |
| v3 | Agent-monitored channel with local anomaly detection |
| v4 | Grid-state-aware channel policy |

## Note on Dummy Traffic

Dummy traffic is used to prevent traffic analysis, not to improve throughput.
The KL divergence between real and dummy traffic distributions is monitored
and kept near 0. See `generate_validation.py` for entropy validation.
