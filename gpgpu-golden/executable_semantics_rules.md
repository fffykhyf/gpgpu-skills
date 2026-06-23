# Executable Semantics Rules

Every executable rule must be derived from `SYSTEM_CONTRACT_IR` and emitted into
`GOLDEN_CONTRACT_MODEL`. The golden model executes contract paths; it does not
define new policy.

## Execution Semantics

Base required execution functions:

| Semantics function | Required contract path |
|---|---|
| `select_warp` | `execution_model.scheduler` |
| `update_active_mask` | `execution_model.simt.active_mask_rule` |
| `apply_scoreboard_dependency` | `execution_model.scoreboard` |

Feature-gated execution functions:

| Feature gate | Required when enabled | Required when disabled |
|---|---|---|
| `execution_model.features.simt_divergence` | `resolve_divergence` | documented non-goal |
| `execution_model.features.visible_pipeline_commit` | `commit_pipeline_visible_state` | documented non-goal |

## Memory Semantics

Base required memory functions:

| Semantics function | Purpose |
|---|---|
| `address_space_resolve` | Map an address to global, shared, local, constant, or invalid space. |
| `coalesce` | Convert lane memory intents into reference memory transactions. |
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
| `grid_block_thread_map` | Map grid and block dimensions to logical threads and warps. |
| `kernel_entry_resolve` | Resolve the program image entry point. |
| `completion_or_fault_observe` | Produce observable completion or fault state. |

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
