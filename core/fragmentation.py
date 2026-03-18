import os
import random
import hashlib
from core.packet import Packet
from core.signature import SignatureEngine


# ── XOR-AONT helpers ──────────────────────────────────────────────────────────
# Based on Rivest (1997) All-or-Nothing Transform.
# Every fragment is XORed with a pad derived from a random key K.
# K itself is XORed with H(fragments) and appended as the final fragment.
# Recovering ANY strict subset F' ⊂ F leaks zero information about M
# (mutual information I(M; F') ≤ ε under uniform input distribution).

def _pad_to(data: bytes, length: int) -> bytes:
    """Zero-pad data to exactly `length` bytes."""
    return data.ljust(length, b'\x00')


def _xor(a: bytes, b: bytes) -> bytes:
    """XOR two equal-length byte strings."""
    return bytes(x ^ y for x, y in zip(a, b))


def _block_pad(key: bytes, index: int, size: int) -> bytes:
    """Deterministic per-block pad: SHA-256(key || index) truncated to size."""
    raw = hashlib.sha256(key + index.to_bytes(4, 'big')).digest()
    # Repeat to cover sizes > 32 bytes
    repeated = (raw * (size // 32 + 1))[:size]
    return repeated


def aont_split(data: bytes, n: int) -> list:
    """
    Split `data` into n+1 AONT blocks.
    Blocks 0..n-1 are XOR-masked real fragments.
    Block n is the AONT key block (K XOR H(masked_blocks)).
    Returns list of n+1 byte strings, all of length `block_size`.
    """
    # Pad data so it divides evenly into n blocks
    block_size = max(1, (len(data) + n - 1) // n)
    padded = _pad_to(data, block_size * n)

    # Random AONT key
    K = os.urandom(block_size)

    # Mask each block: masked_i = block_i XOR PRF(K, i)
    masked = []
    for i in range(n):
        block = padded[i * block_size:(i + 1) * block_size]
        masked_block = _xor(block, _block_pad(K, i, block_size))
        masked.append(masked_block)

    # Key block: K XOR H(masked_0 || masked_1 || ... || masked_{n-1})
    h = hashlib.sha256(b''.join(masked)).digest()
    h_padded = _pad_to(h, block_size)
    key_block = _xor(K, h_padded)

    return masked + [key_block]


def aont_recover(blocks: list) -> bytes:
    """
    Recover original data from n+1 AONT blocks.
    Requires ALL n+1 blocks. Returns None if any block is missing.
    """
    if not blocks:
        return None

    n = len(blocks) - 1          # number of real fragment blocks
    key_block = blocks[-1]
    masked = blocks[:-1]
    block_size = len(key_block)

    # Recover K: K = key_block XOR H(masked_0 || ... || masked_{n-1})
    h = hashlib.sha256(b''.join(masked)).digest()
    h_padded = _pad_to(h, block_size)
    K = _xor(key_block, h_padded)

    # Unmask each block
    data = b''
    for i, masked_block in enumerate(masked):
        block = _xor(masked_block, _block_pad(K, i, block_size))
        data += block

    return data


# ── Public API ────────────────────────────────────────────────────────────────

def fragment_message(data: bytes, n_fragments: int, dummy_ratio: float, key: bytes) -> list:
    """
    Fragment `data` into n_fragments + 1 AONT packets plus dummy packets.

    AONT guarantee (Proposition 1):
        For all strict subsets F' ⊂ F with |F'| < N+1,
        I(M; F') ≤ ε  (negligible under uniform input distribution).

    The (n_fragments+1)th packet is the AONT key block — required for recovery.
    Dummy packets are computationally indistinguishable from real fragments (L3).
    All packets are signed with `key` (L1 integrity).
    """
    signer = SignatureEngine()
    msg_id = os.urandom(8)
    fragments = []

    # ── L2: AONT split into n_fragments real blocks + 1 key block ────────────
    aont_blocks = aont_split(data, n_fragments)
    total_real = len(aont_blocks)          # = n_fragments + 1
    block_size = len(aont_blocks[0])

    for i, block in enumerate(aont_blocks):
        pkt = Packet.create(msg_id, i, total_real, block, False)
        pkt.signature = signer.sign(pkt.signable(), key)
        fragments.append(pkt)

    # ── L3: Dummy packets — same size, same format, indistinguishable ─────────
    dummy_count = int(n_fragments * dummy_ratio)
    for i in range(dummy_count):
        dummy_payload = os.urandom(block_size)
        pkt = Packet.create(msg_id, total_real + i, total_real, dummy_payload, True)
        pkt.signature = signer.sign(pkt.signable(), key)
        fragments.append(pkt)

    # Shuffle: adversary cannot distinguish real from dummy by position
    random.shuffle(fragments)
    return fragments


def reconstruct_message(packets: list, key: bytes) -> bytes:
    """
    Recover original message from AONT packets.
    Requires ALL non-dummy packets (total_real = n_fragments + 1).
    Returns None (⊥) if any real fragment is missing — all-or-nothing.
    """
    signer = SignatureEngine()

    # Filter dummies and verify signatures
    real_pkts = []
    for p in packets:
        if p.is_dummy:
            continue
        if not signer.verify(p.signable(), p.signature, key):
            continue                       # forged packet → discard
        real_pkts.append(p)

    if not real_pkts:
        return None

    total_real = real_pkts[0].total_frags

    # Check all fragments present
    received_ids = {p.frag_id for p in real_pkts}
    if len(received_ids) < total_real:
        return None                        # incomplete → ⊥ (fail-secure, L5/L7)

    # Reconstruct in order
    ordered = sorted(real_pkts, key=lambda p: p.frag_id)
    blocks = [p.payload for p in ordered]

    return aont_recover(blocks)
