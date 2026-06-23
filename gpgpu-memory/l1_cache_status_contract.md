# L1 Cache Status Contract

Cache status values:

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

Never merge cache misses with reservation failures.

