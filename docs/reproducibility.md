# Reproducibility

## Environment
- Python 3.13 with the exact versions in `requirements.txt`
  (`pip install -r requirements.txt`). `cryptography` 50.0.1 ships a
  statically linked OpenSSL (4.0.2 in the pinned build); the TLS baseline needs a
  Python whose `ssl` module is linked against OpenSSL ≥ 3.5 (ML-KEM groups and
  ML-DSA certificates). `scripts/verify_all.sh` checks both.
- No GPU, no network access and no paid resources are needed.

## One command
```
./scripts/verify_all.sh           # environment, compile, tests, mutation smoke, result provenance, manuscript numbers, figures
./scripts/verify_all.sh --smoke   # additionally runs every experiment runner on a reduced configuration (results go to a temporary directory)
```
Each stage reports PASS / FAIL / SKIPPED / NOT RUN / BLOCKED; embedded-hardware
measurement is reported BLOCKED because no device is available.

## Re-running an experiment
```
python3 experiments/runners/exp002_crypto_bench.py experiments/configs/EXP-002_crypto_bench.json
python3 experiments/runners/exp003_reliability.py experiments/configs/EXP-003_reliability.json
python3 experiments/runners/exp004_partial_capture.py experiments/configs/EXP-004_partial_capture.json
python3 experiments/runners/exp005_traffic_capture.py experiments/configs/EXP-005_traffic_capture.json
python3 experiments/runners/exp006_traffic_attacker.py experiments/configs/EXP-006_traffic_attacker.json
python3 experiments/runners/exp007_cap_detection.py experiments/configs/EXP-007_cap_detection.json
python3 experiments/runners/exp008_cyberphysical_agc.py experiments/configs/EXP-008_cyberphysical_agc.json
python3 experiments/runners/exp009_protocol_baselines.py experiments/configs/EXP-009_protocol_baselines.json
python3 experiments/runners/exp005_traffic_capture.py experiments/configs/EXP-010_decoupled_shaping.json
python3 experiments/runners/exp006_traffic_attacker.py experiments/configs/EXP-011_attacker_on_decoupled.json
python3 experiments/runners/exp008_cyberphysical_agc.py experiments/configs/EXP-012_agc_antiwindup.json
python3 experiments/runners/exp013_tls_chain_matched.py experiments/configs/EXP-013_tls_chain_matched.json
python3 experiments/runners/exp008_cyberphysical_agc.py experiments/configs/EXP-014_actuator_headroom.json
python3 scripts/paper_values.py      # manuscript numbers -> results/paper_values.json
python3 scripts/make_figures.py      # figures/*.png (600 dpi), *.pdf, *.csv, FIGURE_SOURCES.csv
python3 scripts/make_diagrams.py     # figures/diagrams/*.drawio (+ PNG/PDF)
```
Set `AEGIS_RESULTS_DIR` to write runs elsewhere. Seeds are in the configs.
Stochastic experiments (EXP-003/004/006/007/008/011/012/014) reproduce exactly from
their seeds on the pinned versions; timing experiments (EXP-002/005/009/010/013)
reproduce in distribution only and will differ on other hardware.

## Measured run times on the reference VM (from environment.json / status.json)
EXP-002 0.3 min; EXP-003 0.1 min; EXP-004 0.1 min; EXP-005 33 min; EXP-006 6 min;
EXP-007 1.9 min; EXP-008 16 min; EXP-009 3 min; EXP-010 25.1 min; EXP-011 2.9 min;
EXP-012 14.9 min (ran concurrently with the failed EXP-011 attempt); EXP-013 0.1 min.
