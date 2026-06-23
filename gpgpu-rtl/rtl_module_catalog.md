# RTL Module Catalog

The catalog enumerates RTL modules and template obligations for a minimal
self-correcting SIMT GPGPU. The machine-readable catalog lives in
`shared/tables/rtl_module_catalog.yaml`.

## Core Modules

| Module | Required responsibility |
|---|---|
| `command_processor_or_launch_frontend` | Bind host/runtime launch commands into device-visible dispatch state. |
| `workgroup_dispatcher` | Allocate SM/warp slots, launch context, and workgroup rank metadata. |
| `sm_top` | Own SM-level control and dispatch boundaries. |
| `warp_scheduler` | Bind scheduler contract to selected warp. |
| `fetch_snapshot_unit` | Capture scheduled PC, mask, and identity before fetch latency. |
| `decode_unit` | Bind contract-derived decode table to instruction class and operands. |
| `decode_issue_unit` | Bind ISA decode, execute, and writeback paths. |
| `scoreboard` | Bind reserve/release hazards and final-packet release. |
| `operand_collector` | Bind RF read timing, packetization, and bank conflicts. |
| `register_file` | Bind register read/write ports and hazards. |
| `writeback_commit` | Bind final writeback, byte enables, EOP, and scoreboard release event. |
| `warp_control_unit` | Bind TMC/WSPAWN/SPLIT/JOIN/PRED/BAR/WSYNC control payloads. |
| `split_join_unit` | Bind divergence stack push/pop and reconvergence restore. |
| `barrier_unit` | Bind barrier arrival, wait, phase, and release state. |
| `simt_stack` | Bind divergence and reconvergence state when enabled. |
| `csr_runtime_interface` | Bind runtime-visible control/status interface. |

## Memory Path Modules

| Module | Required responsibility |
|---|---|
| `load_store_queue` | Bind memory request issue, replay, tags, stalls, and retire. |
| `lsu_slice` | Bind lane address, byte enable, data formatting, and LSU packet identity. |
| `memory_scheduler` | Bind non-blocking tags, request queues, response assembly, and replay. |
| `coalescer` | Bind lane masks, byte enables, and coalesced transaction formation. |
| `memory_coalescer` | Bind original lane shape, tag restore, and response-shape restoration. |
| `l1_cache_bank` | Bind bank mapping, MSHR tags, replay ordering, and almost-full gating. |
| `l1_cache_wrapper` | Bind bank tag expansion, response demux, and backend support matrix. |
| `local_memory_bank` | Bind LDS/local memory bank conflicts, response routing, and backpressure. |
| `lds_bank_unit` | Bind LDS bank selection and bank conflict stalls. |
| `l1_cache_or_global_adapter` | Bind cache/global request-response behavior and global fallback. |
| `memory_response_router` | Bind response tags, wakeup routing, and replay/fault routing. |
| `cache_response_router` | Bind response demux, warp/lane restore, final-EOP scoreboard release, and cache/MSHR response routing. |
| `fault_completion_unit` | Bind completion, trap, poison, and runtime-visible fault reporting. |
| `fabric_router` | Bind SM source identity, L2 slice routing, virtual channels, ordering scope, and queue backpressure. |
| `interconnect` | Bind module-to-module transport or memory fabric adapter. |
| `l2_cache_slice` | Bind slice/bank lookup, miss allocation, fill/replay handoff, and response demux target. |
| `l2_mshr` | Bind miss context retention, fill completion, replay order, release, and deadlock guard. |
| `dram_controller` | Bind DRAM channel/bank/row scheduling, conflict attribution, and response order. |
| `atomic_unit` | Bind atomic serialization point, old/new value visibility, and response routing. |
| `fence_drain_unit` | Bind scope-specific visibility drain and completion after required visibility. |
| `barrier_unit` | Bind barrier arrival, phase, LSU drain requirement, and release bitmap. |
| `wsync_drain_unit` | Bind prior-work drain, pending operation counters, and release after drain. |
| `trace_adapter` | Bind module-local trace taps into `NORMALIZED_TRACE_IR` fields. |

Every catalog entry must have contract paths, interface definitions, required
local state, required trace fields, partial simulation gates, and timing checks.
The machine-readable template must use these exact keys:

```yaml
required_contract_paths:
required_local_state:
required_input_interfaces:
required_output_interfaces:
required_partial_sim_cases:
required_trace_fields:
forbidden_hidden_state:
timing_checks:
```

## Forbidden Shortcuts

- Do not merge `coalescer` into `load_store_queue` unless the selected template
  explicitly declares that fusion and still exposes coalescing trace fields.
- Do not merge fault reporting into a memory adapter without a
  `fault_completion_unit` equivalent.
- Do not release scoreboard entries from raw memory responses before
  response-shape restoration and final EOP.
- Do not hide fabric route, L2 slice, MSHR, DRAM bank, atomic serialization,
  fence visibility, barrier phase, or WSYNC drain state outside traceable
  module-local state.
- Do not use full-system simulation as evidence for missing module partial sim.
- Do not define interface semantics here; consume
  `SYSTEM_CONTRACT_IR.interface_semantics_model` and emit
  `INTERFACE_BINDING_IR`.
