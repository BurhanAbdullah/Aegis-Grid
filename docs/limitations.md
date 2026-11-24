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
6. **AONT bound** is computational (random-oracle model), weak for short shards,
   and relevant only after session-key exposure.
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
