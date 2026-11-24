"""Minimal grid PKI with ML-DSA X.509 certificates.

Validation performed by ``validate_peer_cert`` (all must hold):
  1. DER parses as an X.509 v3 certificate.
  2. Signature verifies under the *pinned* CA certificate (single-level chain).
  3. Current time within [notBefore, notAfter].
  4. BasicConstraints present with ca=False (end-entity only).
  5. Subject CN equals the expected peer identity.
  6. Public key algorithm equals the suite's signature algorithm.
Not implemented (ASSUMPTION, see docs/threat_model.md §3): revocation (CRL/OCSP),
multi-level chains, name constraints.
"""
import datetime
from dataclasses import dataclass
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import mldsa
from cryptography.exceptions import InvalidSignature
from .errors import Reject, Reason

_SIG = {"ML-DSA-44": (mldsa.MLDSA44PrivateKey, mldsa.MLDSA44PublicKey),
        "ML-DSA-65": (mldsa.MLDSA65PrivateKey, mldsa.MLDSA65PublicKey),
        "ML-DSA-87": (mldsa.MLDSA87PrivateKey, mldsa.MLDSA87PublicKey)}


def _name(cn):
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


def _utc(ms):
    return datetime.datetime.fromtimestamp(ms / 1000.0, tz=datetime.timezone.utc)


@dataclass
class Credential:
    identity: str
    sig_alg: str
    key: object          # ML-DSA private key
    cert_der: bytes


class GridCA:
    def __init__(self, name="Aegis-Grid Root CA", sig_alg="ML-DSA-65", now_ms=None, days=365):
        self.sig_alg = sig_alg
        self.key = _SIG[sig_alg][0].generate()
        now = _utc(now_ms) if now_ms is not None else datetime.datetime.now(datetime.timezone.utc)
        self.cert = (x509.CertificateBuilder().subject_name(_name(name)).issuer_name(_name(name))
                     .public_key(self.key.public_key()).serial_number(x509.random_serial_number())
                     .not_valid_before(now - datetime.timedelta(minutes=5))
                     .not_valid_after(now + datetime.timedelta(days=days))
                     .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
                     .sign(self.key, None))

    def issue(self, identity: str, sig_alg: str = "ML-DSA-65", now_ms=None, valid_s=86400,
              ca_flag=False) -> Credential:
        key = _SIG[sig_alg][0].generate()
        now = _utc(now_ms) if now_ms is not None else datetime.datetime.now(datetime.timezone.utc)
        cert = (x509.CertificateBuilder().subject_name(_name(identity)).issuer_name(self.cert.subject)
                .public_key(key.public_key()).serial_number(x509.random_serial_number())
                .not_valid_before(now - datetime.timedelta(seconds=60))
                .not_valid_after(now + datetime.timedelta(seconds=valid_s))
                .add_extension(x509.BasicConstraints(ca=ca_flag, path_length=None), critical=True)
                .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False,
                                             key_encipherment=False, data_encipherment=False,
                                             key_agreement=False, key_cert_sign=ca_flag, crl_sign=False,
                                             encipher_only=False, decipher_only=False), critical=True)
                .sign(self.key, None))
        return Credential(identity, sig_alg, key, cert.public_bytes(serialization.Encoding.DER))


def validate_peer_cert(der: bytes, ca_cert: x509.Certificate, expected_identity: str,
                       sig_alg: str, now_ms: float):
    try:
        cert = x509.load_der_x509_certificate(der)
    except Exception:
        raise Reject(Reason.BAD_CERT, "unparseable certificate")
    try:
        cert.verify_directly_issued_by(ca_cert)
    except (InvalidSignature, ValueError, TypeError):
        raise Reject(Reason.BAD_CERT, "not issued by pinned CA")
    now = _utc(now_ms)
    if not (cert.not_valid_before_utc <= now <= cert.not_valid_after_utc):
        raise Reject(Reason.CERT_EXPIRED)
    try:
        bc = cert.extensions.get_extension_for_class(x509.BasicConstraints).value
    except x509.ExtensionNotFound:
        raise Reject(Reason.BAD_CERT, "missing basicConstraints")
    if bc.ca:
        raise Reject(Reason.BAD_CERT, "CA certificate presented as end-entity")
    cns = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    if len(cns) != 1 or cns[0].value != expected_identity:
        raise Reject(Reason.WRONG_PEER)
    pub = cert.public_key()
    if not isinstance(pub, _SIG[sig_alg][1]):
        raise Reject(Reason.BAD_CERT, "key algorithm does not match suite")
    return pub
