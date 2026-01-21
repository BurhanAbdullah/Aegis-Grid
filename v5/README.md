Aegis Grid – Version 5 (V5)
Quantum-Adversarial, Unbounded-Compute Threat Model

This version extends Aegis Grid to an adversary with unlimited classical and
quantum computation. V5 abandons cryptographic hardness assumptions and instead
enforces security through time-bounded information-theoretic semantics and
irreversible erasure.

This version is experimental and concept-defining. It is not a replacement
for V3.3, which remains the paper’s primary experimental artifact.

Key idea:
Security does not rely on secrets being hard to compute, but on secrets
ceasing to exist after a bounded time window.
