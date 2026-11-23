"""Typed rejection reasons.

Every failure path in the protocol raises ``Reject`` with one of these codes.
Callers treat any ``Reject`` as M̂ = ⊥.  The exception never carries plaintext,
key material, or partially decrypted data.
"""
import enum


class Reason(enum.Enum):
    MALFORMED = "malformed"
    BAD_VERSION = "bad_version"
    NO_COMMON_SUITE = "no_common_suite"
    DOWNGRADE = "downgrade_detected"
    BAD_CERT = "bad_certificate"
    CERT_EXPIRED = "certificate_expired"
    WRONG_PEER = "wrong_peer_identity"
    BAD_SIGNATURE = "bad_signature"
    BAD_KEY = "invalid_key_material"
    BAD_FINISHED = "bad_finished_mac"
    AUTH_FAIL = "aead_authentication_failed"
    REPLAY = "replay"
    TOO_OLD = "sequence_outside_window"
    WRONG_SESSION = "wrong_session"
    WRONG_EPOCH = "epoch_not_acceptable"
    DEADLINE = "deadline_exceeded"
    SESSION_EXPIRED = "session_expired"
    INCOMPLETE = "insufficient_fragments"
    INTEGRITY = "reconstruction_integrity_failure"
    STATE = "protocol_state_violation"


class Reject(Exception):
    def __init__(self, reason: Reason, detail: str = ""):
        super().__init__(f"{reason.value}: {detail}" if detail else reason.value)
        self.reason = reason
