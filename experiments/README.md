# Experiments

Each registered experiment is one runner in `runners/` and one configuration in
`configs/` with a fixed seed. Several experiments reuse a runner with another
configuration:

| ID | Runner | Configuration |
|---|---|---|
| EXP-002 | `exp002_crypto_bench.py` | `EXP-002_crypto_bench.json` |
| EXP-003 | `exp003_reliability.py` | `EXP-003_reliability.json` |
| EXP-004 | `exp004_partial_capture.py` | `EXP-004_partial_capture.json` |
| EXP-005 | `exp005_traffic_capture.py` | `EXP-005_traffic_capture.json` |
| EXP-006 | `exp006_traffic_attacker.py` | `EXP-006_traffic_attacker.json` |
| EXP-007 | `exp007_cap_detection.py` | `EXP-007_cap_detection.json` |
| EXP-008 | `exp008_cyberphysical_agc.py` | `EXP-008_cyberphysical_agc.json` |
| EXP-009 | `exp009_protocol_baselines.py` (+ `exp009_worker.py`) | `EXP-009_protocol_baselines.json` |
| EXP-010 | `exp005_traffic_capture.py` | `EXP-010_decoupled_shaping.json` |
| EXP-011 | `exp006_traffic_attacker.py` | `EXP-011_attacker_on_decoupled.json` |
| EXP-012 | `exp008_cyberphysical_agc.py` | `EXP-012_agc_antiwindup.json` |
| EXP-013 | `exp013_tls_chain_matched.py` | `EXP-013_tls_chain_matched.json` |
| EXP-014 | `exp008_cyberphysical_agc.py` | `EXP-014_actuator_headroom.json` |

`configs/smoke/` holds reduced configurations used by `scripts/verify_all.sh
--smoke`; their outputs go to a temporary directory and are not results.

Run one experiment from the repository root:

```bash
python3 experiments/runners/exp003_reliability.py experiments/configs/EXP-003_reliability.json
```

A run writes a new directory `results/raw/EXP-0xx/run_<UTC timestamp>/`.
Hypotheses and outcomes are in
[`docs/research_integrity/EXPERIMENT_REGISTER.md`](../docs/research_integrity/EXPERIMENT_REGISTER.md).
