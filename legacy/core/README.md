# core/

Core cryptographic and security primitives for Aegis-Grid.

## Purpose

Implements the cryptographic backbone used across all versions:

- **AES-256-GCM** authenticated encryption
- **Shannon entropy** computation and validation
- **CAP (Cumulative Attack Pressure)** monitoring
- **Adaptive (n, k) thresholding** logic

## Shannon Entropy Mirroring

Messages are validated against an expected entropy distribution.
A message with anomalously low entropy (e.g. constant-value replay attack)
is rejected at the core layer before protocol evaluation.

Target: KL divergence from reference distribution ≈ 0.

## CAP Monitoring

Cumulative Attack Pressure tracks sustained adversarial load over time.
When CAP exceeds threshold, the system tightens acceptance criteria —
it does **not** relax them.

## Relationship to `aegis_grid/core/`

The `aegis_grid/core/` Python package is the executable implementation
of the primitives defined here.
