# v2_model — Adaptive Threshold Model (v2 Analytical Companion)

## Purpose

This directory contains the **mathematical model** underlying v2's adaptive thresholding logic,
separated from the executable v2 research stage.

## Distinction from v2/

| | v2/ | v2_model/ |
|--|-----|-----------|
| Type | Executable simulation | Analytical model |
| Content | Code + config | Equations + derivations |
| Role | Run experiments | Inspect and verify theory |

## Contents

- Threshold adaptation derivations
- CAP (Cumulative Attack Pressure) formal model
- Sensitivity sweep parameters (see `sensitivity_sweep_elastic.sh`)

## Usage

This is a reference artifact. Results here should match the outputs produced by running v2/.
Discrepancies between model predictions and simulation results should be reported as issues.

