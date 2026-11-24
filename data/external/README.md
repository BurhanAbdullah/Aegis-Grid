# External values (not measured in this work)

`pqm4_cortex_m4.csv`: cycle counts copied verbatim from the pqm4 project
(M. J. Kannwischer et al., https://github.com/mupq/pqm4, `benchmarks.md`, read
2026-11-24). pqm4 states that all cycle counts were obtained at 24 MHz on an
Arm Cortex-M4 board (default NUCLEO-L4R5ZI) with arm-none-eabi-gcc 11.3.1.
Rows: fastest Cortex-M4 implementations listed for ML-KEM-768 (m4fspeed) and
ML-DSA-65 (m4f).

`scripts/paper_values.py` combines these with the operation count of the AGP/1
handshake (one ML-DSA-65 signature and two verifications per party; ML-KEM
key generation and decapsulation at the initiator, encapsulation at the
responder). The result is labelled ANALYTICALLY DERIVED from external values;
it excludes hashing, AES-GCM, X.509 parsing and communication, so it is a
lower bound on the cryptographic cost on such a device, not a measurement.
