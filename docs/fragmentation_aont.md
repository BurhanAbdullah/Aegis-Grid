# Fragmentation, All-or-Nothing Transform and Erasure Coding (AGP/1 layer L2)

Status: implemented in `aegis_pq/aont.py`, `aegis_pq/erasure.py`, `aegis_pq/pipeline.py`;
tested in `tests/unit/test_aont.py`, `tests/unit/test_erasure.py`, `tests/integration/test_pipeline.py`;
evaluated in EXP-003 (reliability) and EXP-004 (partial capture).

## 1. Why the original construction was replaced
The legacy `core/fragmentation.py` XORs the message with one pad `K` and sends
`K` as the last fragment. It is not an all-or-nothing transform: every
fragment except the pad is `M_i ⊕ K_i` with the pad bytes reused, and the
reconstruction depends on fragment order. EXP-001 and EXP-004 show that an
observer holding N−1 of N fragments recovers 75 % (N=5) to 96.6 % (N=30) of the
plaintext bytes (SIMULATION RESULT, 2000 trials). The manuscript's statement
that partial fragment sets reveal no information is therefore withdrawn for the
legacy code (DEC-008).

## 2. Construction (package transform with key-hiding block)
Notation: ‖ concatenation, ⊕ XOR, |·| length in bytes.

```
K  ← {0,1}^256 (OS CSPRNG)
X  = u32(|M|) ‖ M ‖ 0^128                   (length field + 16-byte canary)
C  = X ⊕ AES-256-CTR_K(IV = 0^128)
T  = K ⊕ SHA-256(C)
Y  = C ‖ T                                  |Y| = |M| + 52
```
Inverse: `K = T ⊕ SHA-256(C)`, `X = C ⊕ AES-256-CTR_K(0)`, accept only if the
canary is zero and the length field matches; otherwise reject (`INTEGRITY`).

This is Rivest's package transform (FSE 1997) with an OAEP-style last block
(Boyko, CRYPTO 1999); Desai (CRYPTO 2000) analyses CTR-based AONTs.

`Y` is then split by a systematic Reed–Solomon (k, n) code over GF(2^8)
(Cauchy generator, MDS): any k of the n shards reconstruct `Y`, fewer than k
do not determine it. Each shard is carried in its own fixed-size AEAD record
(`msg_id u32 | idx u8 | k u8 | n u8 | |Y| u32 | shard`).

## 3. Security statement (ANALYTICALLY DERIVED)
Model SHA-256 as a random oracle H and AES-256 as a PRF. Let an adversary hold
any k−1 shards (or any proper subset of Y such that at least b bits of Y are
undetermined by its view) and make q queries to H.

*Sketch.* The key K is recoverable only from T ⊕ H(C). If at least b bits of C
∪ T are unknown, the adversary must either query H on the exact C (probability
≤ q·2^(−b) over the unknown bits) or guess T; without K the CTR keystream is
indistinguishable from random up to Adv_prf(AES-256). Hence

    Adv(learn any function of M) ≤ q·2^(−b) + Adv_prf(AES-256).

For an MDS code, k−1 shards leave exactly one shard of f = ⌈|Y|/k⌉ bytes
undetermined, so b = 8f. For a 32-byte message and k=20, f = 5 bytes, b = 40
bits; the bound is then weak (q·2^−40). **The guarantee is computational and
degrades for very short shards.** It is NOT information-theoretic.

## 4. What the layer adds beyond the AEAD
Every record is already AES-256-GCM encrypted under a session key from ML-KEM.
An on-path adversary without that key learns nothing from either 1 or k−1
records, so the AONT adds nothing in that model. The AONT matters only if the
session key is later exposed (endpoint compromise, or harvest-now-decrypt-later
against the key exchange): an adversary that recorded fewer than k shards of a
message still cannot recover any part of it. This is the scope in which the
revised paper states the property.

## 5. Availability trade-off (SIMULATION RESULT, EXP-003)
With k = n (the original all-fragments design), losing one packet destroys the
message. Measured delivery probability, 20 000 Monte-Carlo trials per point,
Wilson 95 % CI (`results/raw/EXP-003/run_20261123T170017Z/delivery_montecarlo.csv`):

| (k, n) | Bernoulli 5 % loss | Gilbert 5 % loss, mean burst 5 |
|---|---|---|
| 5/5 | 0.774 | 0.909 |
| 10/10 | 0.597 | 0.860 |
| 20/20 | 0.354 | 0.776 |
| 30/30 | 0.212 | 0.702 |

Burst loss at the same mean rate is *less* harmful than i.i.d. loss for k = n,
because losses cluster in fewer messages. This contradicts the manuscript's
statement that bursty loss is the harder case for the all-fragments design and
is reported as found.

Erasure coding restores availability under i.i.d. loss (Bernoulli 10 %: 5/7
0.977, 5/8 0.995, 10/15 0.998, 20/28 0.999) but only partly under bursts
(Gilbert 10 %, burst 5: about 0.85–0.91). Two-path round-robin did not improve
delivery under bursts in these runs. Cost: fixed-size records make a 32-byte
message take 395 B at 5/5 and 1876 B at 20/28, versus 83 B for a single
record (`results/raw/EXP-003/run_20261123T170017Z/overhead_and_thresholds.csv`).

The Monte-Carlo abstraction was checked against the real pipeline (sealed
AEAD records, receiver, 3000 messages per case); all four cases have
overlapping 95 % CIs (`results/raw/EXP-003/run_20261123T170017Z/abstraction_check.json`).

## 6. Partial-capture leakage (SIMULATION RESULT, EXP-004)
Fraction of plaintext bytes an observer recovers from k−1 fragments when the
record-layer key is assumed exposed (256-byte random messages, 2000 trials, seed 4242, missing shard filled with zeros; `results/raw/EXP-004/run_20261123T170052Z/partial_capture.csv`):
legacy XOR 0.75–0.966; AONT+RS 0.0039–0.0040 (mean), equal to the chance level
1/256 for byte guessing; maximum in any trial 0.027.

## 7. Limitations
- Computational bound only; weak for very short shards (§3).
- k−1 capture is the threshold; an adversary capturing k shards and the session key recovers M.
- Burst-loss behaviour depends on the loss model; real grid links were not measured.
- Reed–Solomon decoding and the AONT were timed only on the x86-64 VM.
