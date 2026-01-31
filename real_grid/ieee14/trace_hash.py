import hashlib, json

def trace_hash(packet, layers):
    blob = {"packet": packet, "layers": layers}
    return hashlib.sha256(
        json.dumps(blob, sort_keys=True).encode()
    ).hexdigest()
