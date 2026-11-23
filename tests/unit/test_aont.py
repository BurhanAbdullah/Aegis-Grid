import os, random
import pytest
from aegis_pq import aont
from aegis_pq.errors import Reject, Reason


@pytest.mark.parametrize("n", [0, 1, 15, 16, 31, 32, 33, 100, 4096])
def test_roundtrip(n):
    m = os.urandom(n)
    assert aont.inverse(aont.transform(m)) == m


def test_output_length_and_randomisation():
    m = b"A" * 64
    y1, y2 = aont.transform(m), aont.transform(m)
    assert len(y1) == len(m) + aont.OVERHEAD and y1 != y2


@pytest.mark.parametrize("pos", ["first", "middle", "last_key_block"])
def test_any_single_byte_change_is_detected(pos):
    m = os.urandom(200)
    y = bytearray(aont.transform(m))
    i = {"first": 0, "middle": len(y) // 2, "last_key_block": len(y) - 1}[pos]
    y[i] ^= 0x01
    with pytest.raises(Reject) as e:
        aont.inverse(bytes(y))
    assert e.value.reason == Reason.INTEGRITY


def test_missing_block_reveals_no_plaintext_bytes():
    """Adversary knows all of Y except one 16-byte block, guesses it at random:
    recovered plaintext matches M only at chance level (≈1/256 per byte)."""
    rng = random.Random(1)
    matches, total = 0, 0
    for _ in range(300):
        m = bytes(rng.getrandbits(8) for _ in range(256))
        y = bytearray(aont.transform(m))
        j = rng.randrange(0, (len(y) - 32) // 16) * 16
        y[j:j + 16] = bytes(rng.getrandbits(8) for _ in range(16))
        c, t = bytes(y[:-32]), bytes(y[-32:])
        import hashlib
        k = bytes(a ^ b for a, b in zip(t, hashlib.sha256(c).digest()))
        x = aont._ctr(k, c)[4:4 + 256]
        matches += sum(a == b for a, b in zip(x, m)); total += 256
    assert matches / total < 0.01


def test_short_input_rejected():
    with pytest.raises(Reject):
        aont.inverse(b"\x00" * 10)
