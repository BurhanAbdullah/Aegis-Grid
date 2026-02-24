# Canonical Message Definition

All messages evaluated by Aegis-Grid V3-Ledger MUST be reducible to a
canonical byte sequence prior to hashing.

Canonical form (ordered, strict):

1. protocol_version (string)
2. sender_node_id (hex)
3. receiver_node_id (hex)
4. physical_context_id (string)
5. declared_deadline_ns (uint64)
6. payload_length (uint32)
7. payload_bytes (raw)

Rules:
- UTF-8 only
- No whitespace normalization
- No field omission
- No optional fields
- Endianness: big-endian

Any deviation invalidates the message.
