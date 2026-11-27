"""Adversarial and resource-bound tests for the AGP/1 message receiver."""
import pytest

from aegis_pq.channel import SecureChannel, TYPE_DATA
from aegis_pq.errors import Reason, Reject
from aegis_pq.handshake import Initiator, Responder, run_handshake
from aegis_pq.pipeline import FRAG, Receiver, Sender, body_size_for


def endpoints(pki, clock, k=2, n=3, **receiver_limits):
    ca, creds = pki
    ik, rk = run_handshake(
        Initiator("cc-01", "rtu-07", creds["cc-01"], ca.cert, clock),
        Responder("rtu-07", creds["rtu-07"], ca.cert, clock),
    )
    sender = Sender(SecureChannel(ik, clock), k, n)
    receiver = Receiver(SecureChannel(rk, clock), **receiver_limits)
    return sender, receiver


def test_seal_message_uses_one_generation_time(pki, clock):
    sender, receiver = endpoints(pki, clock)
    _, records = sender.seal_message(b"setpoint", 100)
    opened = [receiver.chan.open(record) for record in records]
    assert len({(item[2], item[3]) for item in opened}) == 1


def test_inconsistent_message_deadline_drops_pending_state(pki, clock):
    sender, receiver = endpoints(pki, clock)
    mid, fragments = sender.fragment(b"message")
    t0 = clock.now_ms()
    first = sender.chan.seal(fragments[0], 100, TYPE_DATA, t0)
    second = sender.chan.seal(fragments[1], 100, TYPE_DATA, t0 + 0.25)
    assert receiver.receive(first) is None
    assert receiver.receive(second) is None
    assert mid not in receiver.pending
    assert receiver.rejects[Reason.INTEGRITY] == 1
    assert receiver.pending_bytes == 0


def test_pending_message_count_is_bounded(pki, clock):
    sender, receiver = endpoints(pki, clock, max_pending_messages=1)
    _, first = sender.seal_message(b"first", 100)
    _, second = sender.seal_message(b"second", 100)
    assert receiver.receive(first[0]) is None
    assert receiver.receive(second[0]) is None
    assert len(receiver.pending) == 1
    assert receiver.rejects[Reason.RESOURCE_LIMIT] == 1


def test_pending_byte_budget_is_enforced(pki, clock):
    sender, receiver = endpoints(pki, clock, max_pending_bytes=1)
    _, records = sender.seal_message(b"payload", 100)
    assert receiver.receive(records[0]) is None
    assert receiver.pending == {}
    assert receiver.pending_bytes == 0
    assert receiver.rejects[Reason.RESOURCE_LIMIT] == 1


def test_expire_due_releases_pending_memory(pki, clock):
    sender, receiver = endpoints(pki, clock)
    _, records = sender.seal_message(b"expires", 10)
    assert receiver.receive(records[0]) is None
    assert len(receiver.pending) == 1
    clock.advance(12)
    assert receiver.expire_due() == 1
    assert receiver.pending == {}
    assert receiver.pending_bytes == 0
    assert receiver.rejects[Reason.INCOMPLETE] == 1


def test_conflicting_duplicate_shard_discards_message(pki, clock):
    sender, receiver = endpoints(pki, clock)
    mid, fragments = sender.fragment(b"duplicate")
    t0 = clock.now_ms()
    first = sender.chan.seal(fragments[0], 100, TYPE_DATA, t0)
    altered = bytearray(fragments[0])
    altered[-1] ^= 0x01
    second = sender.chan.seal(bytes(altered), 100, TYPE_DATA, t0)
    assert receiver.receive(first) is None
    assert receiver.receive(second) is None
    assert mid not in receiver.pending
    assert receiver.pending_bytes == 0
    assert receiver.rejects[Reason.INTEGRITY] == 1


def test_delivered_history_fails_closed_at_capacity(pki, clock):
    sender, receiver = endpoints(pki, clock, k=1, n=1, max_delivered_ids=1)
    _, first = sender.seal_message(b"one", 100)
    _, second = sender.seal_message(b"two", 100)
    assert receiver.receive(first[0]) is not None
    assert receiver.receive(second[0]) is None
    assert len(receiver.delivered) == 1
    assert receiver.rejects[Reason.RESOURCE_LIMIT] == 1


def test_sender_refuses_message_id_wraparound(pki, clock):
    sender, _ = endpoints(pki, clock, k=1, n=1)
    sender.next_id = 0xFFFFFFFF
    mid, _ = sender.fragment(b"last id")
    assert mid == 0xFFFFFFFF
    with pytest.raises(Reject) as exc:
        sender.fragment(b"must use a new session")
    assert exc.value.reason == Reason.RESOURCE_LIMIT


def test_sender_message_size_limit(pki, clock):
    sender, _ = endpoints(pki, clock, k=1, n=1)
    sender.max_message_bytes = 4
    with pytest.raises(Reject) as exc:
        sender.fragment(b"12345")
    assert exc.value.reason == Reason.RESOURCE_LIMIT


def test_receiver_rejects_message_above_configured_size(pki, clock):
    sender, receiver = endpoints(pki, clock, k=1, n=1, max_message_bytes=4)
    _, records = sender.seal_message(b"12345", 100)
    assert receiver.receive(records[0]) is None
    assert receiver.pending == {}
    assert receiver.rejects[Reason.RESOURCE_LIMIT] == 1


def test_receiver_rejects_excessive_per_message_shard_storage(pki, clock):
    sender, receiver = endpoints(pki, clock, k=1, n=16, max_message_buffer_bytes=32)
    _, records = sender.seal_message(b"x" * 64, 100)
    assert receiver.receive(records[0]) is None
    assert receiver.pending == {}
    assert receiver.rejects[Reason.RESOURCE_LIMIT] == 1


def test_wire_fragment_count_cannot_exceed_u8(pki, clock):
    with pytest.raises(ValueError):
        endpoints(pki, clock, k=1, n=256)
    with pytest.raises(ValueError):
        body_size_for(100, 256)


def test_body_size_rejects_payload_length_overflow():
    with pytest.raises(ValueError):
        body_size_for(64 * 1024, 1)


def test_deadline_must_fit_wire_microsecond_field(pki, clock):
    sender, _ = endpoints(pki, clock, k=1, n=1)
    with pytest.raises(ValueError):
        sender.seal_message(b"deadline", 5000)
