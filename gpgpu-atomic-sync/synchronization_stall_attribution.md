# Synchronization Stall Attribution

Stable synchronization stall reasons:

- `atomic_wait`
- `atomic_split_or_replay`
- `membar_wait`
- `fence_flush_or_invalidate`
- `barrier_wait`

Each reason requires a synchronization contract event and a release condition.

