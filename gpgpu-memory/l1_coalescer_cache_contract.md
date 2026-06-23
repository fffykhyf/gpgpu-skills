# L1 Coalescer Cache Contract

This contract defines the L1-side obligations for coalesced memory traffic.

Required fields:

- line size
- bank mapping
- MSHR tag expansion
- request queue almost-full gating
- response queue backpressure
- replay ordering
- read/write replay policy

The L1 path must prove whether a request was merged, split, replayed, or
blocked by almost-full state. A cache performance claim is not valid unless the
trace can connect original lane request shape to cache-bank request shape and
then back to restored lane response shape.

Failure modes:

- `COALESCER_RESPONSE_SHAPE_MISMATCH`
- `COALESCER_TAG_RESTORE_MISMATCH`
- `CACHE_REPLAY_ORDER_MISMATCH`
- `WRITE_REPLAY_POLICY_UNDEFINED`
- `READ_REPLAY_POLICY_UNDEFINED`
