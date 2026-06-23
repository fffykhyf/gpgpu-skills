# Execution Semantics

Every executable rule must be derived from `SYSTEM_CONTRACT_IR` and emitted into `GOLDEN_CONTRACT_MODEL`.

## Rule Record

Each rule must define:

- `contract_path`
- `semantics_function`
- `input_fields`
- `output_fields`
- `deterministic_rule_id`
- `failure_mode`

## Required Functions

| Semantics function | Required contract path |
|---|---|
| `select_warp` | `execution_model.scheduler` |
| `update_active_mask` | `execution_model.simt.active_mask_rule` |
| `resolve_divergence` | `execution_model.simt.divergence_rule` |
| `apply_scoreboard_dependency` | `execution_model.scoreboard` |
| `commit_pipeline_visible_state` | `state_model.pipeline_commit` |

## Fail Closed Rules

- Reject if a function has no contract path.
- Reject if a function reads fields outside `SYSTEM_CONTRACT_IR`.
- Reject if a function invents scheduler, warp, or ISA semantics.
