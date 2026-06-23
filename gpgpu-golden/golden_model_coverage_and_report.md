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
