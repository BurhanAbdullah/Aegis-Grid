# AONT and Reed-Solomon layer: security scope and evidence

Status: implemented and tested as a package transform plus systematic Reed-Solomon
(k,n) coding. The construction is not presented as a formally proven AONT.

## 1. Construction retained in v6

The implementation in `aegis_pq/aont.py` computes:

```
K <- {0,1}^256
X = u32(|M|) || M || 0^128
C = X XOR AES-256-CTR_K(0^128)
T = K XOR SHA-256(C)
Y = C || T
```

The output Y is divided into equal-size shards by the systematic Reed-Solomon
implementation in `aegis_pq/erasure.py`. Any k valid shards reconstruct Y.
Each shard is independently protected by the AGP/1 AES-256-GCM record layer.

## 2. Security claims that are supported

- AES-GCM protects each record against an on-path observer who does not know
  the session key, subject to the security of the negotiated suite and correct
  key/nonce management.
- Reed-Solomon coding provides erasure recovery: any k valid, distinct shards
  reconstruct the encoded byte string, subject to the implementation's field
  and matrix assumptions.
- The AONT implementation performs a reversible keyed transform and rejects
  outputs that fail its canary/length check.
- EXP-004 evaluates one specified partial-capture strategy with the record-layer
  session key assumed exposed. The result is empirical evidence for that attack
  and configuration only.

## 3. Claims that are not established

The repository does not currently establish a general theorem that every
proper subset of Reed-Solomon shards reveals zero information about M. In
particular, the earlier proof sketch's inference from "b unknown bits of Y" to
a random-oracle query bound is not a complete reduction for every shard
placement and adversary view. The earlier expression

```
q * 2^(-b) + Adv_prf(AES-256)
```

must not be presented as a proven bound without a corrected formal argument.

The AONT layer therefore receives the status **IMPLEMENTED; EMPIRICALLY
EVALUATED FOR A SPECIFIC ATTACK; GENERAL SECURITY PROOF OPEN**. Do not use
"information-theoretic", "zero leakage", "no information", or "proven secure"
for this layer.

## 4. Threat-model scope

The record AEAD already hides plaintext from an on-path adversary without the
session key. The AONT's intended incremental value concerns a later session-key
exposure combined with incomplete historical packet capture. EXP-004 is a
simulation of one such capture strategy, not a cryptographic proof and not a
complete analysis of all possible partial views.

An adversary obtaining k valid shards and the required transform information
can reconstruct the message. Endpoint compromise, malicious endpoints, side
channels, CA compromise and key revocation remain outside the evaluated scope.

## 5. Evidence and reproducibility

- Implementation: `aegis_pq/aont.py`, `aegis_pq/erasure.py`, `aegis_pq/pipeline.py`.
- Tests: `tests/unit/test_aont.py`, `tests/unit/test_erasure.py`,
  `tests/integration/test_pipeline.py`.
- Experiments: EXP-003 (availability) and EXP-004 (partial-capture simulation).
- Evidence labels: implementation tests, SIMULATION RESULT, and ANALYTICALLY
  DERIVED only where an actual derivation is supplied. No theorem is claimed here.

## 6. Required work before any stronger claim

1. Define the adversary's exact view for every possible k-1 shard subset.
2. Prove a reduction for the actual transform and code, including the cases
   where observed shards contain all or most of the key-hiding block.
3. Include key exposure, oracle access, chosen-message and adaptive-capture
   capabilities explicitly.
4. Validate the proof against exhaustive small-parameter models and targeted
   adversarial tests.
5. Obtain independent cryptographic review before using a formal security claim.
