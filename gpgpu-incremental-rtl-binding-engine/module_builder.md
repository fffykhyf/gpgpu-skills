# Module Builder

The RTL builder constructs `INCREMENTAL_RTL_MAP` module by module.

## Module Record

Each module must declare:

- `module_id`
- `module_kind`
- `consumed_contract_paths`
- `provided_signals`
- `required_signals`
- `latency_contract`
- `local_state_bindings`
- `local_trace_schema`
- `local_simulation_evidence`

## Required Modules

- `sm_core`
- `warp_scheduler`
- `decode_execute_pipeline`
- `register_file`
- `scoreboard`
- `load_store_queue`
- `shared_memory`
- `cache_global_interface`
- `interconnect`
- `csr_runtime_interface`

## Fail Closed Rules

- Reject modules without consumed contract paths.
- Reject provided signals that no downstream interface consumes unless marked debug-only.
- Reject local state bindings that do not map to `SYSTEM_CONTRACT_IR`.
