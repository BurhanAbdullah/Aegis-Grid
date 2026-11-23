import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from aegis_pq.clock import ManualClock
from aegis_pq.pki import GridCA


@pytest.fixture
def clock():
    return ManualClock()


@pytest.fixture
def pki(clock):
    ca = GridCA(now_ms=clock.now_ms())
    creds = {}
    for who in ("cc-01", "rtu-07", "rtu-08"):
        creds[who] = [ca.issue(who, alg, now_ms=clock.now_ms()) for alg in ("ML-DSA-65", "ML-DSA-87", "ML-DSA-44")]
    return ca, creds
