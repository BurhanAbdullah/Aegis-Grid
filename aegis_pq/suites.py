"""Cipher suites for AGP/1 and the negotiation rule.

A suite fixes every algorithm, so there is nothing else to negotiate.
ML-KEM-512 is not offered: the `cryptography` 50.x API exposes only ML-KEM-768
and ML-KEM-1024 (recorded in DECISION_LOG DEC-006).
"""
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric import mlkem, mldsa
from cryptography.hazmat.primitives import hashes


@dataclass(frozen=True)
class Suite:
    code: int
    name: str
    kem: str            # "ML-KEM-768" | "ML-KEM-1024"
    hybrid_x25519: bool  # True: shared secret = ML-KEM ss || X25519 ss
    sig: str            # "ML-DSA-44" | "ML-DSA-65" | "ML-DSA-87"
    aead: str           # "AES-256-GCM"
    hash: str           # HKDF hash
    nist_category: int  # weakest component's NIST PQ category (ASSUMPTION from FIPS 203/204)

    def hash_alg(self):
        return {"SHA-256": hashes.SHA256(), "SHA-384": hashes.SHA384()}[self.hash]

    def kem_generate(self):
        return {"ML-KEM-768": mlkem.MLKEM768PrivateKey, "ML-KEM-1024": mlkem.MLKEM1024PrivateKey}[self.kem].generate()

    def kem_public_from_bytes(self, b: bytes):
        cls = {"ML-KEM-768": mlkem.MLKEM768PublicKey, "ML-KEM-1024": mlkem.MLKEM1024PublicKey}[self.kem]
        return cls.from_public_bytes(b)

    def sig_class(self):
        return {"ML-DSA-44": (mldsa.MLDSA44PrivateKey, mldsa.MLDSA44PublicKey),
                "ML-DSA-65": (mldsa.MLDSA65PrivateKey, mldsa.MLDSA65PublicKey),
                "ML-DSA-87": (mldsa.MLDSA87PrivateKey, mldsa.MLDSA87PublicKey)}[self.sig]


SUITES = {
    0x0101: Suite(0x0101, "AGP1_MLKEM768_MLDSA65_AES256GCM_SHA384", "ML-KEM-768", False, "ML-DSA-65", "AES-256-GCM", "SHA-384", 3),
    0x0102: Suite(0x0102, "AGP1_X25519MLKEM768_MLDSA65_AES256GCM_SHA384", "ML-KEM-768", True, "ML-DSA-65", "AES-256-GCM", "SHA-384", 3),
    0x0201: Suite(0x0201, "AGP1_MLKEM1024_MLDSA87_AES256GCM_SHA384", "ML-KEM-1024", False, "ML-DSA-87", "AES-256-GCM", "SHA-384", 5),
    0x0301: Suite(0x0301, "AGP1_MLKEM768_MLDSA44_AES256GCM_SHA256", "ML-KEM-768", False, "ML-DSA-44", "AES-256-GCM", "SHA-256", 2),
}


@dataclass(frozen=True)
class Policy:
    """Ordered preference (most preferred first) and a floor.

    The responder selects the first suite in *its own* preference order that the
    initiator offered.  The initiator accepts the choice only if it is the first
    suite in the initiator's preference list that the responder supports *and*
    meets the initiator's minimum category; both sides sign the full offered list
    so a stripped ClientHello is detected (see handshake.py).
    """
    preference: tuple
    min_category: int = 3

    def acceptable(self, code: int) -> bool:
        return code in self.preference and SUITES[code].nist_category >= self.min_category


DEFAULT_POLICY = Policy(preference=(0x0101, 0x0102, 0x0201), min_category=3)


def select(responder: Policy, offered: tuple) -> int:
    for code in responder.preference:
        if code in offered and responder.acceptable(code):
            return code
    raise LookupError("no common suite")
