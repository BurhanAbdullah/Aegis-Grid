# Limitations

1. **Hardware.** All timing is from one virtualised x86-64 VM in Python. No RTU, IED,
   PLC or microcontroller was measured (verify_all reports this stage BLOCKED).
   A Cortex-M4 estimate derived from pqm4 cycle counts (`data/external/`) is
   reported in the manuscript as ANALYTICALLY DERIVED from external values, not measured.
2. **Network.** Loopback only; no WAN delay, switching, TSN or wireless effects.
3. **Assumed inputs.** Workload, attack families, channel parameters and frequency
   limits are ASSUMPTIONS (config keys `*_ASSUMPTION`).
4. **Attacker strength.** 33 hand-designed features, window alignment known, four
   classical models; no deep sequence models, no training on the target network.
   Reported AUCs are lower bounds on attacker capability.
5. **Shaping leaks timing** as implemented (EXP-006); indistinguishability is not
   claimed. Shaping at Δ = 2 ms misses the 20 ms event deadline for most event
   messages; Δ = 1 ms costs ×4.3 bandwidth.
6. **AONT security proof is open.** EXP-004 evaluates one partial-capture
   strategy under session-key exposure. The earlier random-oracle bound is not
   a complete reduction for every shard placement and must not be claimed as a
   proven general bound. See `docs/fragmentation_aont.md`.
7. **Detector study** is epoch-level, and its attack families are strong enough
   that all detectors detect them; every detector alarms in benign congestion.
8. **Plant study** covers one test system (IEEE 14-bus), one AGC structure and one
   fallback (hold). Safe hold time is plant- and ramp-dependent; controller
   wind-up must be handled at the sender. The hold-time formula (manuscript Eq. (6))
   is a quasi-steady approximation that overestimated the simulated hold time
   (ratio 0.61–0.88, EXP-014); governor limits did not bind before the band was
   left, but this was checked on this case only. No formal invariant proof.
9. **Time synchronisation** is assumed; an attacker who shifts endpoint clocks
   defeats deadline checks.
10. **Assurance.** Tested, not independently audited or formally verified.
11. **Protection class** (≈3 ms) is out of scope; no suitability claim is made.


12. **Reassembly resources.** The v6.1 candidate bounds pending messages,
    aggregate buffered bytes, per-message shard storage, fragment count and
    delivered-ID history. These defaults require workload-specific sizing.
    The embedding application must schedule `Receiver.expire_due()`; the
    library does not create a background timer. Resource exhaustion rejects
    new messages rather than weakening replay/delivery history.
13. **Protocol assurance.** New v6.1 reassembly changes are a release candidate
    until the full test and CI workflow has passed on the candidate commit.
