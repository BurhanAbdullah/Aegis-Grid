Ledger Interface (Abstract)

The ledger exposes EXACTLY the following operations.

1. register_node(node_id, public_key, metadata_hash)
2. rotate_key(node_id, new_public_key)
3. revoke_node(node_id, reason_hash)
4. commit_message_hash(node_id, message_hash, timestamp_ns)

Constraints:
- All calls are append-only
- No deletion
- No mutation
- No overwrite

Ledger MUST return:
- success
- explicit failure

Silence or timeout = failure.

