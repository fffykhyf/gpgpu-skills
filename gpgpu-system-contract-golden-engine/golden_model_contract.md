# Golden Model Contract

`GOLDEN_CONTRACT_MODEL` is executable reference semantics derived from `SYSTEM_CONTRACT_IR`.

It is not:

- an independent simulator
- a second ISA source of truth
- a second memory-ordering source of truth
- a second launch ABI source of truth

## Required Contents

- `system_contract_ir_hash`
- `execution_semantics_functions`
- `memory_semantics_functions`
- `launch_semantics_functions`
- `config_semantics_functions`
- `contract_path_coverage`
- `forbidden_independent_truth_check`

## Coverage Gate

The model passes only when every required execution, memory, launch, and config contract path is either executable or explicitly non-executable with a documented reason.

## Failure Modes

- `FORBIDDEN_GOLDEN_TRUTH`
- `CONTRACT_PATH_UNMAPPED`
- `GOLDEN_MODEL_COVERAGE_FAIL`
- `NONDETERMINISTIC_REFERENCE_FUNCTION`
