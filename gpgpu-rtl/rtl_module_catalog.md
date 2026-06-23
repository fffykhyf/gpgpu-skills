# RTL Module Catalog

The catalog enumerates RTL modules and template obligations for a minimal
self-correcting SIMT GPGPU. The machine-readable catalog lives in
`shared/tables/rtl_module_catalog.yaml`.

## Core Modules

| Module | Required responsibility |
|---|---|
| `sm_core` | Own SM-level control and dispatch boundaries. |
| `warp_scheduler` | Bind scheduler contract to selected warp. |
| `decode_execute_pipeline` | Bind ISA decode, execute, and writeback paths. |
| `register_file` | Bind register read/write ports and hazards. |
| `scoreboard` | Bind dependency tracking and wakeup behavior. |
| `simt_stack` | Bind divergence and reconvergence state when enabled. |
| `csr_runtime_interface` | Bind runtime-visible control/status interface. |

## Memory Path Modules

| Module | Required responsibility |
|---|---|
| `load_store_queue` | Bind memory request issue, replay, tags, stalls, and retire. |
| `coalescer` | Bind lane masks, byte enables, and coalesced transaction formation. |
| `shared_memory_bank_unit` | Bind shared-memory bank selection and bank conflict stalls. |
| `l1_cache_or_global_adapter` | Bind cache/global request-response behavior and global fallback. |
| `memory_response_router` | Bind response tags, wakeup routing, and replay/fault routing. |
| `fault_completion_unit` | Bind completion, trap, poison, and runtime-visible fault reporting. |
| `interconnect` | Bind module-to-module transport or memory fabric adapter. |

Every catalog entry must have contract paths, interface definitions, required
local state, required trace fields, partial simulation gates, and timing checks.

## Forbidden Shortcuts

- Do not merge `coalescer` into `load_store_queue` unless the selected template
  explicitly declares that fusion and still exposes coalescing trace fields.
- Do not merge fault reporting into a memory adapter without a
  `fault_completion_unit` equivalent.
- Do not use full-system simulation as evidence for missing module partial sim.
- Do not define interface semantics here; consume
  `SYSTEM_CONTRACT_IR.interface_semantics_model` and emit
  `INTERFACE_BINDING_IR`.
