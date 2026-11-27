# Security assumptions (all labelled ASSUMPTION unless stated otherwise)

1. **Primitives.** ML-KEM-768/1024 are IND-CCA2 (FIPS 203), ML-DSA-44/65/87 are EUF-CMA (FIPS 204), AES-256-GCM is a secure AEAD with unique nonces, HKDF-SHA-256/384 is a secure KDF, SHA-256 is used by the implemented transform; no random-oracle AONT theorem is currently claimed. No primitive is implemented in this repository; all come from `cryptography` 50.0.1 (statically linked OpenSSL 4.0.2). The TLS 1.3 baseline uses Python `ssl`, linked against OpenSSL 3.5.9.
2. **Hybrid suite 0x0102.** Session secret is secure if either X25519 or ML-KEM-768 is secure (concatenation combiner fed into HKDF-Extract). ANALYTICALLY argued only; no machine-checked proof.
3. **Custom handshake.** AGP/1 follows the TLS 1.3 signed-transcript + Finished design but has had no external review or formal analysis. It must not be described as provably secure.
4. **PKI.** The grid CA key is uncompromised and pinned at every endpoint; certificates are short-lived; revocation is out of scope.
5. **Endpoints.** Sender and receiver hosts are trusted (no malware, no physical side channels). Software timing side channels of the libraries are out of scope (constant-time behaviour of OpenSSL is assumed, not tested).
6. **Clocks.** Sender and receiver clocks agree within `clock_skew_ms` (default 1 ms). An adversary that can shift either clock can defeat L5; secure time distribution (e.g. IEEE 1588 with security) is assumed.
7. **Randomness.** The OS CSPRNG is sound.
8. **Traffic shaping.** Protects only against a passive observer of timing and size on the path. It cannot hide that a session exists, which endpoints communicate, or load above the shaping capacity.
9. **AONT.** The transform is implemented and EXP-004 evaluates one partial-capture strategy under later session-key exposure. A general security theorem for all shard placements and adversary views is OPEN and must not be claimed (docs/fragmentation_aont.md).
10. **Plant model.** The IEEE 14-bus case with constant-power loads and the Andes default parameters stands in for a real balancing area; frequency limits are illustrative (EXP-008 config).
