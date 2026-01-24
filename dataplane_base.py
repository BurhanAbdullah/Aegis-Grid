import socket
import time
import threading
import os
import psutil
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HOST = "127.0.0.1"
PORT = 9010
MTU = 1400
FRAMES = 100

KEY = AESGCM.generate_key(bit_length=128)
aes = AESGCM(KEY)

def fragment(data, mtu):
    return [data[i:i+mtu] for i in range(0, len(data), mtu)]

def encrypt_packet(pkt):
    nonce = os.urandom(12)
    start = time.perf_counter()
    ct = aes.encrypt(nonce, pkt, None)
    return ct, (time.perf_counter() - start)

def receiver(sock, stats):
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            sock.sendto(b"ACK", addr)
            stats["rx"] += 1
        except:
            break

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    stats = {"rx": 0}
    t = threading.Thread(target=receiver, args=(sock, stats), daemon=True)
    t.start()

    payload = os.urandom(8000)
    frames = fragment(payload, MTU)

    rtts = []
    cryptos = []
    cpu_samples = []

    proc = psutil.Process()

    for _ in range(FRAMES):
        for frame in frames:
            ct, ctime = encrypt_packet(frame)
            cryptos.append(ctime)

            start = time.perf_counter()
            sock.sendto(ct, (HOST, PORT))
            sock.recvfrom(1024)
            rtts.append(time.perf_counter() - start)

            cpu_samples.append(proc.cpu_percent(interval=0.001))

    sock.close()

    print("BASELINE DATA-PLANE RESULTS")
    print(f"avg_rtt_ms: {sum(rtts)/len(rtts)*1000:.4f}")
    print(f"avg_crypto_ms: {sum(cryptos)/len(cryptos)*1000:.4f}")
    print(f"avg_cpu: {sum(cpu_samples)/len(cpu_samples):.2f}")
    print(f"frames_sent: {len(frames)}")

if __name__ == "__main__":
    run()
