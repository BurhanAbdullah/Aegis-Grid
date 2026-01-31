def agc_valid(cmd, grid_state, max_delta_f=0.2):
    """
    cmd = {"type": "AGC", "delta_f": float}
    """
    if cmd["type"] != "AGC":
        return False

    if abs(cmd["delta_f"]) > max_delta_f:
        return False

    # Do not allow AGC if grid already unstable
    if not grid_state["stable"]:
        return False

    return True
