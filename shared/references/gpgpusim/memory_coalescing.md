# Memory Formation and Cache Rules

Memory path order:

```text
lane access
-> warp_memory_transaction
-> coalesced request
-> shared/L1 decision
-> cache status
-> MSHR decision
-> lower memory packet
-> return
-> scoreboard release
```

No cache, L2, or DRAM attribution is valid without a recorded
`warp_memory_transaction` containing lane addresses, active mask, byte mask,
sector mask, transaction address, transaction size, access type, and read/write
or atomic class.

Cache status taxonomy:

- `HIT`
- `HIT_RESERVED`
- `MISS`
- `SECTOR_MISS`
- `MSHR_HIT`
- `RESERVATION_FAIL`

Reservation fail reasons:

- `LINE_ALLOC_FAIL`
- `MISS_QUEUE_FULL`
- `MSHR_ENTRY_FAIL`
- `MSHR_MERGE_ENTRY_FAIL`
- `MSHR_RW_PENDING`

Rule: `MISS` is a locality/cache outcome. `RESERVATION_FAIL` is a structural
resource outcome. They must not be merged.

Raw basis: `raw/gpgpu-sim-memory-hierarchy-and-coalescing-notes.md`.

