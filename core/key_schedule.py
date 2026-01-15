# core/key_schedule.py
import hashlib

def derive_layer_keys(master_key: bytes, nonce: bytes, layers: int = 4):
    """
    Deterministic multilayer key derivation.
    Abstracts post-quantum KDF in paper.
    """
    keys = []
    material = master_key + nonce
    for _ in range(layers):
        material = hashlib.sha256(material).digest()
        keys.append(material)
    return keys
