# Golden Semantics

## Merged Source Material

### Source: `skill/gpgpu-contract/executable_semantics_rules.md`

# Executable Semantics Rules

Every executable rule must be derived from `SYSTEM_CONTRACT_IR` and emitted into
`GOLDEN_CONTRACT_MODEL`. The golden model executes contract paths; it does not
define new policy.

## Execution Semantics

Base required execution functions:

| Semantics function | Required contract path |
|---|---|
| `dispatch_workgroup_to_warps` | `launch_model.grid_block_thread_mapping` |
| `capture_fetch_snapshot` | `execution_model.scheduler.fetch_snapshot_rule` |
| `select_warp` | `execution_model.scheduler` |
| `apply_exec_mask_write` | `execution_model.simt.exec_mask_write_rule` |
| `apply_predicate_mask` | `execution_model.simt.predicate_mask_rule` |
| `update_active_mask` | `execution_model.simt.active_mask_rule` |
| `scoreboard_reserve` | `execution_model.scoreboard.reserve_rule` |
| `scoreboard_release_on_final_packet` | `execution_model.scoreboard.release_rule` |
| `rf_read_lane_vector` | `state_model.register_file_state.read_rule` |
| `rf_writeback_lane_vector` | `state_model.register_file_state.writeback_rule` |

Feature-gated execution functions:

| Feature gate | Required when enabled | Required when disabled |
|---|---|---|
| `execution_model.features.simt_divergence` | `resolve_split`, `resolve_join` | documented non-goal |
| `execution_model.features.visible_pipeline_commit` | `commit_pipeline_visible_state` | documented non-goal |

## Memory Semantics

Base required memory functions:

| Semantics function | Purpose |
|---|---|
| `address_space_resolve` | Map an address to global, shared, local, constant, or invalid space. |
| `coalesce` | Convert lane memory intents into reference memory transactions. |
| `coalescer_request_shape` | Record original lane shape, byte enables, offsets, and request tag. |
| `coalescer_response_restore` | Restore lane-shaped response data, masks, byte enables, and final EOP. |
| `byte_enable` | Compute byte enables from lane mask, access size, and address alignment. |
| `request_lifecycle_step` | Advance issue, stall, response, replay, retire, or fault state. |

Feature-gated memory functions:

| Feature gate | Required when enabled | Required when disabled |
|---|---|---|
| `memory_model.fence.enabled` | `fence_order` | `reject_fence_or_trap` with unsupported reason |
| `memory_model.atomic.enabled` | `atomic_apply` | `reject_atomic_or_trap` with unsupported reason |

If `SYSTEM_CONTRACT_IR.memory_model.atomic.enabled = false`, the contract must
document why atomics are unsupported and the golden model must implement
`reject_atomic_or_trap`, not `atomic_apply`.

## Launch Semantics

Required launch functions:

| Semantics function | Purpose |
|---|---|
| `abi_decode` | Decode launch arguments from the ABI layout. |
| `launch_abi_decode` | Trace each public ABI field into device dispatch or explicit unsupported behavior. |
| `grid_block_thread_map` | Map grid and block dimensions to logical threads and warps. |
| `kernel_entry_resolve` | Resolve the program image entry point. |
| `completion_or_fault_observe` | Produce observable completion or fault state. |
| `completion_fault_observe` | Emit pass/fail evidence for done, fault, timeout, and host-visible status. |

## Sync Semantics

Required synchronization functions:

| Semantics function | Purpose |
|---|---|
| `apply_barrier_arrive` | Record arrival event, participant set, phase, and optional async token. |
| `apply_barrier_wait` | Park and release warps according to barrier phase, wait mask, and drain rules. |
| `apply_wsync_drain` | Wait for prior warp work to retire without modifying EXEC mask. |

## Config Semantics

Required config functions:

| Semantics function | Purpose |
|---|---|
| `classify_config_visibility` | Classify config fields as ABI, private, simulator, test, or debug. |
| `validate_config_owner` | Reject duplicate config owners and hidden defaults. |

## Interface Semantics

Required interface functions:

| Semantics function | Required contract path |
|---|---|
| `request_accept_lifecycle` | `interface_semantics_model.request_acceptance` |
| `payload_stability_when_not_ready` | `interface_semantics_model.payload_stability` |
| `tag_uniqueness_until_response` | `interface_semantics_model.tag_uniqueness` |
| `response_ordering_by_tag` | `interface_semantics_model.response_ordering` |
| `fault_response_retirement` | `interface_semantics_model.fault_response` |

## Rule Record Format

Each rule record must define:

- `contract_path`
- `semantics_function`
- `input_fields`
- `output_fields`
- `deterministic_rule_id`
- `feature_gate` if conditional
- `unsupported_reason` if disabled-feature handling is required
- `failure_mode`

## Fail-Closed Rules

- Reject if a function has no contract path.
- Reject if a function reads fields outside `SYSTEM_CONTRACT_IR`.
- Reject if a function invents scheduler, warp, ISA, memory, launch, config, or
  interface semantics.
- Reject hidden memory ordering defaults.
- Reject duplicate request behavior not declared in the contract.
- Reject ABI fields not present in `SYSTEM_CONTRACT_IR.launch_model`.
- Reject grid/block dimensions that cannot map to declared execution resources.
- Reject completion behavior that cannot be observed by runtime-visible state.

## XiangShan Live Reference API Rules

`GOLDEN_REF_API` must expose a live step interface suitable for RTL
synchronization:

- `gpgpu_ref_init`
- `gpgpu_ref_memcpy`
- `gpgpu_ref_statecpy`
- `gpgpu_ref_step_event`
- `gpgpu_ref_query_event`
- `gpgpu_ref_status`

The live synchronization unit must be explicit: instruction, warp event, memory
transaction, sync event, or CTA event. Offline profiling and checkpoint calls
must be separate optional entry points so the basic diff path remains light.

### Source: `skill/gpgpu-contract/golden_model_coverage_and_report.md`

# Golden Model Coverage and Report

`GOLDEN_CONTRACT_MODEL` is executable reference semantics derived from
`SYSTEM_CONTRACT_IR`.

It is not:

- an independent simulator
- a second ISA source of truth
- a second memory-ordering source of truth
- a second launch ABI source of truth
- a second scheduler, config, or interface lifecycle source of truth

## Required Contents

- `system_contract_ir_hash`
- `execution_semantics_functions`
- `memory_semantics_functions`
- `launch_semantics_functions`
- `config_semantics_functions`
- `interface_semantics_functions`
- `contract_path_coverage`
- `feature_gate_coverage`
- `forbidden_independent_truth_check`

## Contract Path Coverage

The model passes only when every required execution, memory, launch, config, and
interface contract path is executable or explicitly non-executable with a
documented reason.

Coverage gates must support feature-gated requirements:

- `simt_divergence` requires `resolve_divergence` only when enabled.
- `visible_pipeline_commit` requires `commit_pipeline_visible_state` only when
  enabled.
- `memory_model.atomic.enabled = true` requires `atomic_apply`.
- `memory_model.atomic.enabled = false` requires `reject_atomic_or_trap` and a
  documented unsupported reason.
- `memory_model.fence.enabled = true` requires `fence_order`.
- `memory_model.fence.enabled = false` requires `reject_fence_or_trap` and a
  documented unsupported reason.

## Forbidden Independent Truth Check

The golden model must not contain independent:

- ISA definitions or opcode tables
- memory ordering overrides
- launch ABI overrides
- scheduler overrides
- config defaults
- interface lifecycle overrides

All such fields must be absent or derived from an explicit
`SYSTEM_CONTRACT_IR` path.

## Report Requirements

`CONTRACT_SEMANTICS_REPORT` must include:

- verdict
- `system_contract_ir_hash`
- `golden_contract_model_hash`
- executable semantics coverage
- feature-gate coverage
- failed contract paths
- forbidden independent truth check

## Failure Modes

- `FORBIDDEN_GOLDEN_TRUTH`
- `CONTRACT_PATH_UNMAPPED`
- `GOLDEN_MODEL_COVERAGE_FAIL`
- `NONDETERMINISTIC_REFERENCE_FUNCTION`
- `FEATURE_GATE_COVERAGE_FAIL`

## XiangShan Golden Coverage Additions

Coverage must prove that `GOLDEN_REF_API`, `ARCHITECTURE_STATE_BLOB`,
`GOLDEN_SIDECAR_STATE`, `STORE_COMMIT_EVENT`, and `GOLDEN_STATUS_API` are
defined when live diff is enabled. The report must state whether the golden
model is being used in live diff mode or offline analysis mode.

### Source: `skill/gpgpu-contract/module_twin_model_rules.md`

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

### Source: `skill/gpgpu-contract/simt_golden_trace_spec.md`

# SIMT Golden Trace Spec

Golden SIMT traces must include:

- warp id;
- PC;
- active mask;
- reconvergence PC;
- call depth;
- divergence event;
- reconvergence event.

SIMT trace checks are independent from scoreboard dependency checks.

## XiangShan-Inspired State Blob Fields

`ARCHITECTURE_STATE_BLOB` must include per-warp PC, active mask,
reconvergence state, warp status, lane predicate state, and trap/fault state.
`GOLDEN_SIDECAR_STATE` may include scoreboard and outstanding memory state for
trace alignment, but SIMT correctness must compare only architecture-visible
state and events.

### Source: `skill/gpgpu-contract/memory_transaction_golden_spec.md`

# Memory Transaction Golden Spec

Golden memory semantics must expose coalescer input before cache timing:

- lane addresses;
- active mask;
- byte mask;
- sector mask;
- access type;
- read/write/atomic class;
- transaction grouping.

The golden model may validate transaction functional content without adopting a
timing cache, MSHR, NoC, or DRAM model.

## Store Commit Channel

Every committed store must be observable through `STORE_COMMIT_EVENT` with
cycle or step, SM, warp, lane mask, address, byte enable, data hash, and commit
sequence. Store mismatch localization must use this channel before falling back
to final memory dumps.

### Source: `skill/gpgpu-contract/atomic_fence_barrier_golden_spec.md`

# Atomic / Fence / Barrier Golden Spec

Atomic semantics must define request issue, lane participation, return value,
destination register, serialization domain, completion event, and scoreboard
release condition.

Fence semantics must define scope, ordering domain, affected memory spaces,
visibility point, completion condition, and cache flush/invalidate policy.

Barrier semantics must define CTA id, participant count, arrival mask, waiting
warp list, release condition, and release event.

GPGPU-Sim timing notes are not a complete memory consistency model.

### Source: `skill/gpgpu-contract/memory_path_executable_semantics.md`

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

### Source: `skill/gpgpu-contract/sync_atomic_executable_semantics.md`

# Synchronization and Atomic Executable Semantics

Golden synchronization semantics must distinguish atomic, fence, barrier, and
WSYNC behavior.

Required functions:

- `execute_atomic_serialization()`
- `execute_fence_drain()`
- `execute_barrier_arrive_wait_release()`
- `execute_wsync_drain()`

Rules:

- Atomic visibility is not fence visibility.
- Fence is not barrier arrival.
- Barrier release does not imply memory visibility unless explicitly frozen.
- WSYNC drains prior work and is not a scoreboard hazard.
