import time

def within_time_window(packet_time, window_ms):
    return (time.time() - packet_time) * 1000 <= window_ms
