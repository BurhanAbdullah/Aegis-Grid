import os
from typing import List

def aont_fragment(data: bytes, n_fragments: int) -> List[bytes]:
    if n_fragments < 2:
        raise ValueError("Need at least 2 fragments")

    K = os.urandom(len(data))
    masked = bytes([d ^ k for d, k in zip(data, K)])

    chunk_size = len(masked) // (n_fragments - 1)
    fragments = [
        masked[i*chunk_size:(i+1)*chunk_size]
        for i in range(n_fragments - 2)
    ]
    fragments.append(masked[(n_fragments - 2)*chunk_size:])
    fragments.append(K)

    return fragments

def aont_reconstruct(fragments: List[bytes]) -> bytes:
    K = fragments[-1]
    masked = b''.join(fragments[:-1])
    return bytes([m ^ k for m, k in zip(masked, K)])
