# Module Twin Model Rules

Module twins mirror RTL-visible module contracts for first-divergence analysis.
They are derived from `SYSTEM_CONTRACT_IR`; they are not independent simulators.

Required twin boundaries:

- `lsu_slice`
- `memory_scheduler`
- `memory_coalescer`
- `local_memory_bank`
- `l1_global_adapter`
- `l2_cache_slice`
- `l2_mshr`
- `cache_response_router`
- `fabric_router`
- `dram_controller`
- `atomic_unit`
- `fence_drain_unit`
- `barrier_unit`
- `wsync_drain_unit`

Every twin trace must carry `contract_path`, `rtl_module_path`, `instruction_uuid`,
`sm_id`, `warp_id`, lane or request tags, and `evidence_hash`.
