def update_pressure(current, physics_ok):
    if physics_ok:
        return max(0.0, current - 0.2)
    return min(10.0, current + 1.0)
