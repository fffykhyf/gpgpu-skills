# Observable Trace Contract

RTL trace must expose, when implemented:

- cycle;
- core id;
- warp id;
- PC;
- active mask;
- issue valid;
- non-issue reason;
- scoreboard collision;
- selected pipe;
- memory transaction count;
- cache status;
- ICNT status;
- L2 queue status;
- DRAM queue status;
- writeback release.

These fields feed `gpgpu-simppa`; they are not optional for performance claims.

## XiangShan Structured Trace Tables

When a feature affects memory, scheduling, synchronization, atomics, NoC, cache,
or performance, RTL must define a `STRUCTURED_TRACE_TABLE` with schema version,
producer, write gate, common fields, and consumer skill. Required table
families include `WARP_ISSUE_LOG`, `WARP_COMMIT_LOG`, `SCOREBOARD_LOG`,
`MEMORY_TRANSACTION_LOG`, `COALESCER_LOG`, `CACHE_ACCESS_LOG`,
`MSHR_EVENT_LOG`, `NOC_PACKET_LOG`, `BARRIER_EVENT_LOG`, `FENCE_EVENT_LOG`,
`ATOMIC_EVENT_LOG`, and `COUNTER_SNAPSHOT_LOG`.
