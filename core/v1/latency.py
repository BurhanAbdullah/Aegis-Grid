# v1.0.0 Deterministic Invariant
LATENCY_BOUND = 0.100 # Hard 100ms bound
def check_bound(measured):
    return measured <= LATENCY_BOUND
