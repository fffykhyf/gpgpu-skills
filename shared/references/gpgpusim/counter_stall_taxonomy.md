# Counter and Stall Taxonomy

Counter status classes:

- `producer-backed`: source path emits or updates the counter.
- `defined-only`: enum, printer, schema, or declaration exists, but producer is
  not proven.
- `parser-only`: visualization/parser variable exists without producer proof.

Stable stall reasons:

- `idle_control`
- `ibuffer_empty`
- `simt_redirect`
- `scoreboard_wait`
- `pipe_unavailable`
- `barrier_wait`
- `membar_wait`
- `atomic_wait`
- `shared_bank_conflict`
- `coalescing_stall`
- `cache_miss`
- `cache_reservation_fail`
- `mshr_fail`
- `icnt_req_backpressure`
- `icnt_return_backpressure`
- `l2_queue_full`
- `dram_queue_full`
- `dram_timing_wait`
- `return_path_stall`
- `scoreboard_release_wait`

Root-cause reports must cite producer-backed counters for stable conclusions.
Defined-only and parser-only counters can explain gaps or motivate producer
patches, but cannot be the sole regression gate.

Raw basis: `raw/gpgpu-sim-counter-and-stall-reason-taxonomy.md`.

