# v2.0 Reconstruction Rule

Validity Window:
validity_window = 5ms

Reconstruction Rule:
reconstruction_result = 1 if packet_loss == 0
reconstruction_result = 0 otherwise

This model is deterministic and piecewise-defined.
