def rocof(prev, curr, dt, limit=1.0):
    if prev is None:
        return True
    rate = abs(curr["freq"] - prev["freq"]) / dt
    return rate <= limit
