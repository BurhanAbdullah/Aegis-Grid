import time

def constant_entropy_send(packets, rate_hz=100):
    interval = 1.0 / rate_hz
    for p in packets:
        time.sleep(interval)
        yield p
