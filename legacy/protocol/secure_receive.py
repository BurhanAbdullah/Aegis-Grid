import time
from core.crypto.ca import ROOT_CA
from core.crypto.encryption import decrypt

MAX_SKEW = 5  # seconds

def secure_receive(packet, aes_key):
    node_id, signature = packet.cert

    # 1. Verify certificate
    if not ROOT_CA.verify_certificate(node_id, signature):
        raise SecurityError("Invalid certificate")

    # 2. Verify timestamp freshness
    if abs(time.time() - packet.timestamp) > MAX_SKEW:
        raise SecurityError("Replay or delayed packet")

    # 3. Verify & decrypt
    plaintext = decrypt(
        aes_key,
        packet.ciphertext,
        packet.nonce,
        packet.tag
    )

    return plaintext
