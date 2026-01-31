def gps_valid(packet_ts, grid_ts, max_skew=0.05):
    return abs(packet_ts - grid_ts) <= max_skew
