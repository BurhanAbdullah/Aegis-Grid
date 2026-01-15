from dataclasses import dataclass
import time
import uuid

@dataclass
class Packet:
    packet_id: str
    payload: bytes
    is_dummy: bool
    timestamp: float
    signature: bytes

    @staticmethod
    def create(payload: bytes, is_dummy: bool, signature: bytes):
        payload = payload.ljust(256, b'\x00')[:256]
        return Packet(
            packet_id=str(uuid.uuid4()),
            payload=payload,
            is_dummy=is_dummy,
            timestamp=time.time(),
            signature=signature
        )
