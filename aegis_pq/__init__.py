"""aegis_pq — remediation implementation of the Aegis-Grid message path.

Modules
-------
errors      typed rejection reasons (no partial plaintext is ever returned)
clock       injectable monotonic/wall clock (tests control time explicitly)
suites      cipher-suite registry and negotiation policy
pki         ML-DSA X.509 certificate authority and validation
handshake   AGP/1 authenticated ML-KEM handshake and key schedule
channel     record layer: AES-256-GCM, nonces, sequence numbers, replay window,
            deadlines, key update (rekey) and session expiry
aont        package-transform all-or-nothing transform (M3)
erasure     systematic Reed-Solomon (k-of-n) erasure code over GF(2^8) (M3)
pipeline    message -> AONT -> erasure code -> fixed-size encrypted packets (M3)

All cryptographic primitives come from the `cryptography` package (statically linked
OpenSSL 4.0 in the pinned build). Nothing here implements ML-KEM, ML-DSA, AES or SHA-2 from scratch.
"""
__version__ = "6.0.0-dev"
