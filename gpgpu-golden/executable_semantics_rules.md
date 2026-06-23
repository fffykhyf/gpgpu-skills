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
