import socket
import time
import threading
import os
import psutil
import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Network config
HOST = "127.0.0.1"
PORT = 9009
MTU = 1400

# Crypto
KEY = AESGCM.generate_key(bit_length=128)
aes = AESGCM(KEY)

MODEL_LOAD = {
    "AegisGrid": 1,
    "EncryptedOnly": 3,
    "IEC62351": 5,
    "IDSAdaptive": 4,
}

def fragment(data, mtu=MTU):
    return [data[i:i+mtu] for i in range(0, len(data), mtu)]

def encrypt_packet(pkt):
    nonce = os.urandom(12)
    start = time.perf_counter()
    ct = aes.encrypt(nonce, pkt, None)
    return nonce + ct, (time.perf_counter() - start)

def server(stop_flag):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(0.5)

    while not stop_flag["stop"]:
        try:
            data, addr = sock.recvfrom(4096)
            sock.sendto(b"ACK", addr)
        except socket.timeout:
            pass

    sock.close()

def run_test(system, payload_size=10000):
    burst = MODEL_LOAD.get(system, 2)

    stop_flag = {"stop": False}
    t = threading.Thread(target=server, args=(stop_flag,), daemon=True)
    t.start()

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    payload = os.urandom(payload_size)
    frames = fragment(payload)

    rtts = []
    crypto_times = []
    cpu_samples = []

    for _ in range(burst):
        for frame in frames:
            enc, crypto_time = encrypt_packet(frame)
            crypto_times.append(crypto_time)

            start = time.perf_counter()
            client.sendto(enc, (HOST, PORT))
            client.recvfrom(4096)
            rtts.append(time.perf_counter() - start)

            cpu_samples.append(psutil.cpu_percent(interval=None))

    stop_flag["stop"] = True
    t.join(timeout=1)
    client.close()

    return {
        "avg_rtt_ms": (sum(rtts) / len(rtts)) * 1000,
        "avg_crypto_ms": (sum(crypto_times) / len(crypto_times)) * 1000,
        "avg_cpu": sum(cpu_samples) / len(cpu_samples),
        "frames_sent": len(rtts),
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 dataplane_test.py <ModelName>")
        sys.exit(1)

    system = sys.argv[1]
    results = run_test(system)

    for k, v in results.items():
        print(f"{k}: {v:.4f}")
