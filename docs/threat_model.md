# Threat Model and System Scope (revision 2026-11)

This document replaces the informal adversary hierarchy (AP/AA/AD/AQ) of the
original manuscript with explicit capabilities, exclusions and application scope.
Status labels follow the research-integrity rules (ASSUMPTION, ANALYTICALLY
DERIVED, SIMULATION RESULT, HARDWARE MEASUREMENT).

## 1. System model

| Element | Definition in this study |
|---|---|
| Sender | A control-centre or substation-gateway process (e.g. EMS/AGC dispatcher) that issues set-point or control messages. |
| Receiver | A field-side process (RTU, IED gateway, DER controller) that applies the control action to a plant. |
| Channel | A single logical unicast path over an IP network (UDP datagrams). Optional second path for multipath experiments. Loss/delay are modelled (Bernoulli, Gilbert–Elliott, fixed + random delay) or produced by the local OS loopback stack. |
| Network adversary | Controls the channel between sender and receiver (Dolev–Yao style on that path), with the capabilities in §2. |
| Smart-grid application | Supervisory / secondary-control set-points (e.g. AGC raise/lower, DER set-points) and PMU-based wide-area control signals with deadlines of tens to hundreds of milliseconds. See §4. |
| Control centre / field devices | Endpoints are general-purpose processes; no embedded hardware was available (see §6). |
| Trusted | Endpoint code, endpoint long-term ML-DSA signing keys, the grid certificate authority (CA) key, endpoint clocks within the stated skew. |
| Untrusted | Everything on the network path, including routers and any on-path middlebox. |
| Key management | A grid CA (ML-DSA-65) issues X.509 certificates binding an endpoint identity to its ML-DSA public key. CA certificate is pinned at each endpoint. Revocation is **not implemented** (ASSUMPTION: short-lived certificates). |
| Time synchronisation | Endpoints share a clock with bounded skew `ε_clk` (ASSUMPTION; in deployment provided by IEEE 1588 PTP or GNSS). Deadline checks reject generation times beyond `now + ε_clk` and expired messages beyond `t_gen + D + ε_clk`. Clock attacks are out of scope (§3). |
| Failure conditions | Packet loss, delay beyond deadline, corruption, replay, authentication failure, session expiry, handshake failure. Each maps to message rejection (⊥) and, at the plant, to the fallback controller. |

## 2. Adversary capabilities

| Capability | In scope? | How it is evaluated |
|---|---|---|
| Observe all traffic on the path | Yes | Traffic-analysis experiments (M4) |
| Capture/record packets indefinitely ("harvest now, decrypt later") | Yes | Motivates ML-KEM; AONT partial-capture argument (M3) |
| Modify packets | Yes | AEAD rejection tests (M2) |
| Inject packets | Yes | Forgery/malformed-packet tests (M2) |
| Replay packets | Yes | Replay-window tests (M2) |
| Delay packets | Yes | Deadline tests (M2), delay-injection scenarios (M5/M6) |
| Drop packets (selectively or in bursts) | Yes | Loss/availability experiments (M3), DoS discussion |
| Reorder packets | Yes | Reordering tests (M2/M3) |
| Timing analysis (inter-arrival times) | Yes | Attacker classifiers (M4) |
| Traffic-volume analysis (sizes, counts, bursts) | Yes | Attacker classifiers (M4) |
| Adaptive attacks (react to system behaviour) | Partially | Detector evaluated on held-out attack families (M5); no learning adversary |
| Quantum computation against recorded key exchanges | Yes, as a motivation; ML-KEM/ML-DSA security is ASSUMED from FIPS 203/204 | Not tested (cannot be) |
| Compromise endpoints | **No** | Excluded (§3) |
| Compromise long-term credentials | Only *after* a session ends (forward secrecy argument) | Analytic (protocol spec §7) |
| Compromise network infrastructure | Equivalent to on-path adversary above | — |
| Link-saturating DoS / jamming | Modelled only as loss/delay; not prevented | Availability quantified, not defended |

## 3. Exclusions (not protected)

1. Compromised sender or receiver hosts, malicious insiders, or malicious firmware.
2. Side channels inside endpoints (power, EM, cache timing of the crypto library).
3. Attacks on time synchronisation (PTP/GNSS spoofing). The deadline check is only as good as the clock.
4. Denial of service: an adversary that drops enough packets always prevents delivery. The design trades availability for integrity and freshness; availability under loss is measured, not guaranteed.
5. Certificate revocation, CA compromise, and key storage (HSM/TPM) — assumed, not implemented.
6. Implementation-level cryptographic correctness of OpenSSL's ML-KEM/ML-DSA (trusted library).
7. Physical-layer attacks on the plant and false-data injection into measurements that are correctly authenticated by a compromised sensor.

## 4. Application latency scope

The original manuscript motivated the design with sub-4 ms GOOSE trip messages
but evaluated a 50 ms budget. This revision evaluates each traffic class
separately and claims support only where measured.

| Class | Typical transfer-time requirement (source) | Evaluated here? |
|---|---|---|
| Protection trips (IEC 61850 GOOSE/SV, type 1A / P1–P3) | ≈3 ms class (IEC 61850-5 transfer-time classes; values to be cited from the standard in the manuscript) | Measured as a stress point only; **no suitability claim** unless the measured pipeline meets it. Fixed-rate emission with N fragments adds ≥(N−1)·Δ by construction. |
| Critical substation messaging (interlocks, fast automation) | ≈10–20 ms class | Measured; claim only if met |
| PMU-based wide-area control (IEEE C37.118 streams) | tens of ms | Measured (primary target) |
| Supervisory control / AGC set-points (SCADA) | 100 ms – seconds | Measured (primary target); plant study (M6) uses AGC |
| Monitoring / non-critical telemetry | seconds | Covered by the above |

## 5. Security goals and their evidence class

| Goal | Mechanism | Evidence class |
|---|---|---|
| Confidentiality and integrity of control messages against a recording, quantum-capable adversary | ML-KEM key establishment + AES-256-GCM | ASSUMPTION (primitive security) + tests of correct composition |
| Mutual authentication | ML-DSA-65 signatures over the handshake transcript; X.509 certificates from a pinned CA | Tests (M2) |
| Replay / reordering / freshness | Per-epoch sequence numbers, sliding replay window, authenticated deadline field | Tests (M2) |
| Partial-capture resilience | Package-transform + RS(k,n) (M3) | SIMULATION RESULT for one specified capture strategy (EXP-004); general security proof OPEN |
| Traffic-analysis resistance | Fixed-size packets, fixed-rate emission, encrypted dummy packets | SIMULATION/EMULATION RESULT on loopback (M4); no indistinguishability claim |
| Fail-secure behaviour | Rejected/late messages never actuate; fallback controller | SIMULATION RESULT on a named power-system model (M6) |

## 6. Hardware scope

All measurements are taken on a virtualised x86-64 Intel Xeon (2.1 GHz, 4 vCPU)
running Linux. No ARM Cortex-M, RTU or IED hardware was available. Published
embedded benchmarks are cited only as external reference values, never as
measurements of this implementation.
