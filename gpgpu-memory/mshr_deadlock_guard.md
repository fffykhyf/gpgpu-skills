# MSHR Deadlock Guard

Cache and coalescer pipelines must declare structural guards before accepting a
request that can allocate downstream resources.

Required guards:

- `mshr_alm_full`
- `request_queue_alm_full`
- `response_queue_alm_full`
- no request accepted unless the response path can eventually drain

The guard must be part of the contract, trace, and unit-test evidence. A design
that only detects deadlock after timeout must emit `MSHR_DEADLOCK_GUARD_MISSING`.

Acceptance evidence:

- directed test with nearly full MSHR
- directed test with nearly full request queue
- directed test with response backpressure
- trace showing accepted request count never exceeds guaranteed drain capacity
