# AGP/1 — Aegis-Grid Protocol Specification (implementation `aegis_pq`, v6.1 candidate)

Status: **IMPLEMENTED AND TESTED** in the recorded v6.0 baseline. The v6.1
candidate adds bounded message reassembly and new adversarial regression tests;
these changes require a fresh CI run before they are marked verified.
Not independently reviewed; not formally verified.

## 1. Layering

```
application control message M (bytes, ≤ 60 KiB default sender/receiver limit)
 └─ L2  package transform (general security proof open)         aegis_pq/aont.py      (Milestone 3)
     └─ erasure code, k-of-n (systematic Reed–Solomon)       aegis_pq/erasure.py   (Milestone 3)
         └─ L3  one fragment per fixed-size AGP/1 record     aegis_pq/channel.py
             └─ L4  fixed-rate emission with dummy records   aegis_pq/shaping.py    (Milestone 4)
                 └─ UDP
L1  session keys for all records come from the AGP/1 handshake  aegis_pq/handshake.py
L5  deadline field in every record, checked on receipt
L6  detector / parameter policy                               aegis_pq/detectors.py  (Milestone 5)
L7  fallback controller at the plant interface                experiments (Milestone 6)
```

## 2. Primitives (all from `cryptography` 50.0.1, statically linked OpenSSL 4.0.2)

| Function | Primitive | Standard |
|---|---|---|
| Key establishment | ML-KEM-768 or ML-KEM-1024; optional hybrid with X25519 | FIPS 203; RFC 7748 |
| Entity authentication | ML-DSA-44/65/87 (pure mode, empty context) | FIPS 204 |
| Certificates | X.509 v3 signed with ML-DSA by a pinned grid CA | RFC 5280 profile (subset, §6) |
| KDF | HKDF with SHA-256 or SHA-384 | RFC 5869 |
| Record protection | AES-256-GCM, 96-bit nonce, 128-bit tag | NIST SP 800-38D |
| Handshake MAC | HMAC-SHA-256/384 ("Finished") | RFC 2104 |

ML-KEM-512 is not offered because the library does not expose it (DEC-006).

## 3. Cipher suites and negotiation

| Code | Name | KEM | Signature | Hash | NIST cat. |
|---|---|---|---|---|---|
| 0x0101 | AGP1_MLKEM768_MLDSA65_AES256GCM_SHA384 | ML-KEM-768 | ML-DSA-65 | SHA-384 | 3 |
| 0x0102 | AGP1_X25519MLKEM768_MLDSA65_AES256GCM_SHA384 | X25519 + ML-KEM-768 (hybrid) | ML-DSA-65 | SHA-384 | 3 |
| 0x0201 | AGP1_MLKEM1024_MLDSA87_AES256GCM_SHA384 | ML-KEM-1024 | ML-DSA-87 | SHA-384 | 5 |
| 0x0301 | AGP1_MLKEM768_MLDSA44_AES256GCM_SHA256 | ML-KEM-768 | ML-DSA-44 | SHA-256 | 2 |

Default policy: preference (0x0101, 0x0102, 0x0201), floor category 3, so 0x0301
is never negotiated unless both sides lower the floor. The deployment is
**natively post-quantum** (0x0101/0x0201) or **hybrid** (0x0102); it is not
layered on top of TLS.

Negotiation: the initiator offers an ordered suite list and one key share per
KEM it is willing to use. The responder picks the first offered suite (initiator
order) it accepts and has a share for, and returns its own supported list. The
initiator accepts only if the pick equals its most-preferred offered suite that
the responder supports and for which it sent a share; otherwise `DOWNGRADE`.
Both signatures cover the full transcript, so a modified ClientHello fails
signature verification at the initiator (test `test_downgrade_stripping_rejected`).

## 4. Handshake

```
Initiator I                                              Responder R
ClientHello: ver, rand_I, suites[], shares{KEM: pk_e}, [x25519 pk],
             id_I, id_R                       ───────▶
                                                 validate id_R == self, id_I authorised
                                                 (ss, ct) = ML-KEM.Encaps(pk_e)
                                     ◀───────  ServerHello: ver, rand_R, suite, supported[],
                                                 ct, [x25519 pk], cert_R,
                                                 σ_R = ML-DSA.Sign(sk_R, "AGP1 server CV" ‖ H(CH‖SH_core)),
                                                 Fin_R = HMAC(fk_R, H(CH‖SH_core‖σ_R))
check suite rule; ss = Decaps(ct); erase pk_e secret
validate cert_R (pinned CA, validity, CN = id_R, end-entity, key type)
verify σ_R, Fin_R
ClientFinish: cert_I, σ_I over H(CH‖SH‖CF_core), Fin_I  ───────▶
                                                 validate cert_I (CN = id_I), verify σ_I, Fin_I
```

Key schedule: `PRK = HKDF-Extract(rand_I‖rand_R, ss)`;
`hs = Expand(PRK, "hs"|H(CH‖SH_core))`, `fk_R, fk_I = Expand(hs, "finished R"/"finished I")`;
`ms = Expand(PRK, "ms"|H(CH‖SH‖CF))`; traffic secrets `Expand(ms, "i2r traffic")`,
`Expand(ms, "r2i traffic")`; session id `Expand(ms, "session id")[0:8]`.
Records are accepted by the responder only after ClientFinish verifies.

Measured costs (EXP-002, x86-64 VM, medians, both parties' CPU, no network):
3.4–4.7 ms per handshake depending on suite; 17.0–24.8 kB on the wire. Values
and percentiles are in `results/raw/EXP-002/*/summary_us.csv`. Handshakes run at
session start and on rekey-by-renegotiation only, never per control message.

## 5. Record layer

Header (20 B, AAD): `0xA6 | ver | session_id[8] | epoch u16 | seq u64`.
Body (encrypted): `type | t_gen (µs) | deadline (µs) | len | payload | padding`.
Nonce = per-epoch IV ⊕ (0³²‖seq). Sender never reuses (epoch, seq) and refuses
to send past `rekey_every` without a key update or past the session lifetime.

Key update: `secret_{e+1} = HKDF-Expand(secret_e, "key update")` after
`rekey_every` records (default 2¹⁶). The receiver derives epoch e+1 tentatively,
commits it only after a record authenticates under it, keeps one previous epoch
for reordering, and erases older keys.

Replay protection: per-epoch sliding window, W = 1024 (default), updated only
after successful authentication. Late records consume their sequence number,
so a delayed record cannot be replayed later.

Deadline: accept iff `now ≤ t_gen + deadline + ε_clk`. `ε_clk` defaults to 1 ms
(ASSUMPTION about PTP-grade synchronisation).

Session expiry: default 1 h or 2³² records; afterwards both directions refuse.

## 6. Message reassembly and resource limits (v6.1 candidate)

The wire fragment header is `msg_id:u32 | index:u8 | k:u8 | n:u8 | ylen:u32`.
Because `n` is encoded in one byte, the wire protocol supports at most 255
fragments (indices 0 through 254 for n=255), even though the Reed-Solomon
implementation can construct a 256-row matrix. A sender must not wrap a
32-bit message ID within a session; it must establish a new session instead.

The default sender and receiver message limit is 60 KiB. The receiver also
bounds concurrent incomplete messages, aggregate buffered shard bytes,
per-message shard storage, fragment count and delivered-message history.
When delivered-history capacity is reached, the receiver fails closed rather
than evicting IDs and weakening the exactly-once guarantee within the session.
A resource-limit rejection is not a successful delivery.

Every fragment belonging to one message must carry identical authenticated
generation time and deadline values. The sender stamps all fragments from one
message with one generation time. Conflicting metadata or conflicting content
for a repeated shard index discards the incomplete message.

Incomplete messages expire at `t_gen + deadline + clock_skew`. The caller must
invoke `Receiver.expire_due()` from a periodic timer, including during periods
when no records arrive. `receive()` also performs lazy expiry before processing
each record. The receiver's in-memory limits are defaults for this research
implementation, not universal deployment sizing recommendations.

## 7. Failure handling

Every failure raises `Reject(reason)`; the caller maps it to M̂ = ⊥ and the
plant interface keeps the fallback action (L7). Reasons:
`malformed, bad_version, no_common_suite, downgrade_detected, bad_certificate,
certificate_expired, wrong_peer_identity, bad_signature, invalid_key_material,
bad_finished_mac, aead_authentication_failed, replay, sequence_outside_window,
wrong_session, epoch_not_acceptable, deadline_exceeded, session_expired,
insufficient_fragments, reconstruction_integrity_failure, protocol_state_violation, resource_limit_exceeded`.
A failed handshake object is unusable (state `failed`); no keys are produced.
Rejections never contain plaintext (test `test_reject_carries_no_plaintext`).

## 8. Security properties and their basis

| Property | Basis | Class |
|---|---|---|
| Record confidentiality/integrity | AES-256-GCM with unique nonces; keys from HKDF over ML-KEM secret | ASSUMPTION (primitive security) + tests of nonce uniqueness and tamper rejection |
| Mutual authentication | ML-DSA over full transcript, pinned CA | ASSUMPTION (EUF-CMA of ML-DSA) + tests |
| Forward secrecy vs later long-term key loss | ephemeral ML-KEM key per handshake, erased | ANALYTICALLY DERIVED (design argument); erasure tested in Python object state only — memory zeroisation is not guaranteed in Python |
| Downgrade resistance | transcript signatures + suite rule + floor | tests |
| Replay/freshness | sequence window + authenticated deadline | tests |

Known limitations: no revocation; no formal (e.g. Tamarin/ProVerif) model; Python
cannot guarantee key zeroisation; the handshake is not DoS-hardened (no cookie);
the responder signs before authenticating the initiator. The package-transform
AONT is empirically evaluated for a specific partial-capture strategy, but its
general security proof is open; see `docs/fragmentation_aont.md`.
