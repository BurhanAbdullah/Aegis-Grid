Timing Model:

Let:
T_phys = physical system deadline
T_net  = network delivery bound
T_ledg = ledger finality bound

Constraint:

T_net + T_ledg < T_phys

If violated:
- Message is invalid
- No grace period
- No probabilistic acceptance

Ledger participation is OPTIONAL.
Safety is NOT.
