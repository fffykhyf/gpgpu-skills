# Shared Memory Bank Conflict Contract

Shared memory conflicts are not global memory coalescing.

Required evidence:

- bank mapping function;
- lane-to-bank map;
- conflict count or class;
- broadcast policy;
- stall reason `shared_bank_conflict`;
- release event.

Do not use fixed shared-memory latency as the contract.

