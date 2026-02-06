Ledger Failure Semantics:

- Ledger unavailable → verification impossible
- Verification impossible → message invalid
- Invalid message → dropped without retry

No fallback modes exist.
