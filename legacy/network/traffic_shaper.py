import time

def constant_entropy_send(packets, window_ms=50):
    interval = window_ms / len(packets) / 1000
    for p in packets:
        time.sleep(interval)
        yield p
