# Memory Path Executable Semantics

Golden memory semantics must execute memory-path contracts directly.

Required functions:

- `execute_lsu_lane_format()`
- `allocate_memory_tag()`
- `coalesce_lane_requests()`
- `restore_coalesced_response()`
- `route_request_to_l2_slice()`
- `l1_lookup_or_forward()`
- `l2_lookup_or_allocate_mshr()`
- `l2_fill_and_replay()`
- `schedule_dram_bank()`
- `complete_memory_response()`
- `apply_memory_visibility_event()`

Each function consumes `SYSTEM_CONTRACT_IR` paths and emits trace events that
normalize into `NORMALIZED_TRACE_IR`.
