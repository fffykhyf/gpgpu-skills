# Stall Reason Taxonomy

Stable stall and non-issue reasons for GPGPU skill outputs.

| Reason | Owner stage | Root-cause family | Required evidence |
|---|---|---|---|
| `idle_control` | scheduler | SCHEDULER_ROOT_CAUSE | no eligible warp or control redirect evidence |
| `ibuffer_empty` | scheduler/fetch | SCHEDULER_ROOT_CAUSE | warp valid plus empty ibuffer |
| `simt_redirect` | SIMT | SCHEDULER_ROOT_CAUSE | SIMT top PC mismatch or redirect event |
| `scoreboard_wait` | scoreboard | SCHEDULER_ROOT_CAUSE | collision result and pending destination |
| `pipe_unavailable` | execution pipe | PERFORMANCE_ARCH_ROOT_CAUSE | selected pipe full or unavailable |
| `barrier_wait` | sync | SYNC_ATOMIC_ROOT_CAUSE | barrier arrival mask and release condition |
| `membar_wait` | sync | SYNC_ATOMIC_ROOT_CAUSE | fence scope, drain/visibility condition |
| `atomic_wait` | sync | SYNC_ATOMIC_ROOT_CAUSE | atomic completion token or outstanding count |
| `shared_bank_conflict` | shared memory | MEMORY_SYSTEM_ROOT_CAUSE | bank mapping and conflict count |
| `coalescing_stall` | coalescer | MEMORY_SYSTEM_ROOT_CAUSE | transaction amplification or access queue wait |
| `cache_miss` | cache | CACHE_MSHR_ROOT_CAUSE | HIT/MISS/SECTOR_MISS status |
| `cache_reservation_fail` | cache/MSHR | CACHE_MSHR_ROOT_CAUSE | reservation fail reason |
| `mshr_fail` | MSHR | CACHE_MSHR_ROOT_CAUSE | MSHR allocation or merge failure |
| `icnt_req_backpressure` | ICNT request path | FABRIC_ROOT_CAUSE | request `has_buffer` false or push stall |
| `icnt_return_backpressure` | ICNT return path | FABRIC_ROOT_CAUSE | return FIFO or memory-to-shader stall |
| `l2_queue_full` | L2/subpartition | MEMORY_SYSTEM_ROOT_CAUSE | named L2 queue occupancy |
| `dram_queue_full` | DRAM ingress | DRAM_ROOT_CAUSE | L2-to-DRAM or DRAM queue full |
| `dram_timing_wait` | DRAM scheduler | DRAM_ROOT_CAUSE | timing blocker or row/bank scheduling evidence |
| `return_path_stall` | response path | FABRIC_ROOT_CAUSE | return queue or response FIFO full |
| `scoreboard_release_wait` | writeback/release | SCHEDULER_ROOT_CAUSE | response arrived but destination not released |

