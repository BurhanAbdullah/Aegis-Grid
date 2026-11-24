"""TLS 1.3 baseline (Python ssl, linked OpenSSL 3.5) with ML-DSA or ECDSA certificates.

Python 3.13 has no SSLContext.set_groups, so the key-exchange group is chosen
with an OpenSSL configuration file (OPENSSL_CONF, `Groups = ...`) in a child
process, and the negotiated group is *verified* by parsing the key_share
extension of the ServerHello bytes (not assumed).
"""
import datetime, os, ssl, struct
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import mldsa, ec

GROUP_IDS = {0x001d: "x25519", 0x0017: "secp256r1", 0x0201: "MLKEM768", 0x0202: "MLKEM1024", 0x11ec: "X25519MLKEM768"}

OPENSSL_CONF_TEMPLATE = """openssl_conf = openssl_init
[openssl_init]
ssl_conf = ssl_sect
[ssl_sect]
system_default = system_default_sect
[system_default_sect]
Groups = {groups}
"""


def make_pki(directory, sig="mldsa65", cn="rtu-07"):
    now = datetime.datetime.now(datetime.timezone.utc)
    gen = {"mldsa65": mldsa.MLDSA65PrivateKey.generate, "p256": lambda: ec.generate_private_key(ec.SECP256R1())}[sig]
    def cert(subject, key, ikey, iname, ca):
        b = (x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject)]))
             .issuer_name(iname).public_key(key.public_key()).serial_number(x509.random_serial_number())
             .not_valid_before(now - datetime.timedelta(minutes=5)).not_valid_after(now + datetime.timedelta(days=30))
             .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True))
        if not ca:
            b = b.add_extension(x509.SubjectAlternativeName([x509.DNSName(subject)]), critical=False)
        return b.sign(ikey, None if sig == "mldsa65" else hashes.SHA256())
    cak = gen(); can = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "grid-ca")])
    cac = cert("grid-ca", cak, cak, can, True); sk = gen(); sc = cert(cn, sk, cak, can, False)
    ck = gen(); cc = cert("cc-01", ck, cak, can, False)          # client certificate for mutual TLS
    p = lambda n: os.path.join(directory, f"{sig}_{n}")
    open(p("cli.pem"), "wb").write(cc.public_bytes(serialization.Encoding.PEM))
    open(p("cli.key"), "wb").write(ck.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                                    serialization.NoEncryption()))
    open(p("ca.pem"), "wb").write(cac.public_bytes(serialization.Encoding.PEM))
    open(p("srv.pem"), "wb").write(sc.public_bytes(serialization.Encoding.PEM))
    open(p("srv.key"), "wb").write(sk.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                                    serialization.NoEncryption()))
    return p("ca.pem"), p("srv.pem"), p("srv.key")


def contexts(ca, crt, key, mutual=False, leaf_only=False):
    """Server/client contexts. mutual=True requires and verifies a client certificate
    (matched to AGP/1, which always authenticates both parties).

    With mutual=True and the default leaf_only=False, OpenSSL builds each sender's
    certificate chain from its own verify store, which then contains the CA, so the
    5.4 kB ML-DSA-65 CA certificate is sent in both directions (auto-chaining; Python
    offers no switch to disable it). leaf_only=True matches AGP/1, which sends only the
    end-entity certificate: each side trusts the peer's end-entity certificate directly
    (X509 partial-chain trust, i.e. leaf pinning instead of CA validation). It is used
    only to measure handshake bytes with equal chain lengths (EXP-013)."""
    s = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); s.minimum_version = ssl.TLSVersion.TLSv1_3
    s.load_cert_chain(crt, key)
    s.num_tickets = 0        # no session resumption tickets: AGP/1 has no resumption (matched setting);
                             # OpenSSL tickets would otherwise carry the client certificate (~16 kB extra with ML-DSA-65)
    c = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT); c.minimum_version = ssl.TLSVersion.TLSv1_3
    cli, clik = crt.replace("srv.pem", "cli.pem"), key.replace("srv.key", "cli.key")
    if leaf_only:
        if not mutual:
            raise ValueError("leaf_only applies to mutual authentication")
        for x in (s, c):
            x.verify_flags |= ssl.VERIFY_X509_PARTIAL_CHAIN
        c.load_verify_locations(crt)
        s.verify_mode = ssl.CERT_REQUIRED; s.load_verify_locations(cli)
        c.load_cert_chain(cli, clik)
        return s, c
    c.load_verify_locations(ca)
    if mutual:
        s.verify_mode = ssl.CERT_REQUIRED; s.load_verify_locations(ca)
        c.load_cert_chain(cli, clik)
    return s, c


def server_hello_group(sh: bytes):
    """Return the key_share group id from a TLS record containing a ServerHello."""
    if sh[0] != 22 or sh[5] != 2:
        raise ValueError("not a ServerHello record")
    body = sh[9:]
    p = 2 + 32
    p += 1 + body[p]          # legacy_session_id
    p += 3                    # cipher suite + compression
    (extl,) = struct.unpack(">H", body[p:p + 2]); p += 2
    end = p + extl
    while p < end:
        t, l = struct.unpack(">HH", body[p:p + 4])
        if t == 51:
            return struct.unpack(">H", body[p + 4:p + 6])[0]
        p += 4 + l
    raise ValueError("no key_share")


def memory_handshake(sctx, cctx, hostname="rtu-07"):
    """In-memory handshake; returns (client_bytes, server_bytes, group_id, cipher)."""
    ci, co, si, so = ssl.MemoryBIO(), ssl.MemoryBIO(), ssl.MemoryBIO(), ssl.MemoryBIO()
    c = cctx.wrap_bio(ci, co, server_hostname=hostname); s = sctx.wrap_bio(si, so, server_side=True)

    def step(o):
        try:
            o.do_handshake(); return True
        except ssl.SSLWantReadError:
            return False
    sh, tot, cd, sd = None, [0, 0], False, False
    for _ in range(10):
        cd = step(c) or cd; a = co.read(); tot[0] += len(a); si.write(a)
        sd = step(s) or sd; b = so.read(); tot[1] += len(b); ci.write(b)
        if b and sh is None:
            sh = b
        if cd and sd and not a and not b:
            break
    return tot[0], tot[1], server_hello_group(sh), c.cipher()[0]
