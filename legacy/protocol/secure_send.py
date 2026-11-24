import time
from core.crypto.ca import ROOT_CA
from core.crypto.encryption import encrypt
from protocol.packet import SecurePacket

MAX_SKEW = 5  # seconds

def secure_send(node_id, plaintext, aes_key):
    timestamp = time.time()

    cert = ROOT_CA.issue_node_certificate(node_id)

    ciphertext, nonce, tag = encrypt(aes_key, plaintext)

    return SecurePacket(
        ciphertext=ciphertext,
        nonce=nonce,
        tag=tag,
        cert=(node_id, cert),
        timestamp=timestamp
    )
