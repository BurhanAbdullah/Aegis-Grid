import itertools, os, random
import numpy as np
import pytest
from aegis_pq import erasure
from aegis_pq.errors import Reject, Reason


def test_field_inverse():
    for a in range(1, 256):
        assert int(erasure.gf_mul(a, erasure.gf_inv(a))) == 1


@pytest.mark.parametrize("k,n", [(1, 1), (1, 3), (3, 3), (4, 6), (5, 8), (10, 13), (20, 25)])
def test_every_k_subset_decodes(k, n):
    rng = random.Random(k * 100 + n)
    data = os.urandom(rng.randint(1, 400))
    sh = erasure.encode(data, k, n)
    assert len(sh) == n and len({len(s) for s in sh}) == 1
    subsets = list(itertools.combinations(range(n), k))
    rng.shuffle(subsets)
    for sub in subsets[:60]:
        assert erasure.decode({i: sh[i] for i in sub}, k, n, len(data)) == data


@pytest.mark.parametrize("k,n", [(4, 6), (10, 13)])
def test_fewer_than_k_rejected(k, n):
    data = os.urandom(100)
    sh = erasure.encode(data, k, n)
    with pytest.raises(Reject) as e:
        erasure.decode({i: sh[i] for i in range(k - 1)}, k, n, len(data))
    assert e.value.reason == Reason.INCOMPLETE


def test_systematic_prefix_is_data():
    data = bytes(range(40))
    sh = erasure.encode(data, 4, 6)
    assert b"".join(sh[:4]) == data


def test_mds_all_square_submatrices_invertible_small():
    g = erasure.generator(4, 8)
    for rows in itertools.combinations(range(8), 4):
        erasure._invert(g[list(rows)])          # raises if singular


def test_malformed_inputs():
    sh = erasure.encode(b"x" * 50, 3, 5)
    with pytest.raises(Reject):
        erasure.decode({0: sh[0], 1: sh[1], 7: sh[2]}, 3, 5, 50)
    with pytest.raises(Reject):
        erasure.decode({0: sh[0], 1: sh[1], 2: sh[2][:-1]}, 3, 5, 50)
