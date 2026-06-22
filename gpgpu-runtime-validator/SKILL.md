---
name: gpgpu-runtime-validator
description: Use when host runtime, software stack, CUDA-like frontend subset, assembler, program image, launch ABI, command queue, completion, fault, and synchronization behavior must be validated against locked contracts.
---

# GPGPU Runtime Validator

## Role

This skill validates host/runtime/launch ABI and software stack behavior. It does not design memory hierarchy or RTL memory path.

## Position in Flow

Upstream:
- gpgpu-artifact-contract-engine RUNTIME_CONTRACT_IR, SOFTWARE_STACK_CONTRACT_IR, PROGRAM_IMAGE_CONTRACT_IR, TEST_APP_CONTRACT_IR, and CONFIG_BINDING_IR
- gpgpu-canonical-state-engine launch_state
- gpgpu-spec-lock ABI_launch_contract

Downstream:
- gpgpu-closure-refinement-engine

## Input IR

Consumes:
- RUNTIME_CONTRACT_IR
- SOFTWARE_STACK_CONTRACT_IR
- PROGRAM_IMAGE_CONTRACT_IR
- TEST_APP_CONTRACT_IR
- CONFIG_BINDING_IR
- GPU_STATE_IR.launch_state
- SPEC_IR.ABI_launch_contract

## Output IR

Produces:
- RUNTIME_VALIDATION_REPORT_IR
- runtime_smoke_trace
- launch_contract_report
- software_stack_contract_report
- program_image_contract_report
- test_app_contract_report

## Owned Decisions

This skill owns:
- frontend_subset_contract
- assembler_contract
- program_image_contract
- kernel_test_app_contract
- golden_output_contract
- Program image loading
- Kernel entry
- Argument layout
- Grid/block dimensions
- Command queue
- Doorbell/start
- Completion/done
- Fault reporting
- CSR/runtime interface
- Host-device synchronization

## Forbidden Actions

This skill must not:
- Design coalescer, load/store queue, cache hierarchy, shared memory banks, request/response tags, or memory RTL pipeline
- Reinterpret ABI fields
- Modify GPU_STATE_IR

## Required Tables

This skill must use:
- shared/tables/runtime_smoke_test_table.yaml
- shared/tables/software_stack_contract_table.yaml
- shared/tables/end_to_end_smoke_test_table.yaml
- shared/tables/config_ownership_table.yaml

## Required Schemas

This skill must validate:
- shared/schemas/runtime_contract_ir.schema.yaml
- shared/schemas/software_stack_contract_ir.schema.yaml
- shared/schemas/program_image_contract_ir.schema.yaml
- shared/schemas/test_app_contract_ir.schema.yaml
- shared/schemas/config_binding_ir.schema.yaml
- shared/schemas/runtime_validation_report_ir.schema.yaml

## Required Invariants

The output must satisfy:
- Launch ABI layout matches SPEC_IR
- Grid/block dimensions fit launch_state
- Completion and fault paths are observable
- Runtime consumes only ABI-visible config
- High-level kernel compilation, assembler output, program image load, parameter binding, output memory dump, and golden checker location agree with the runtime contract

## Failure Modes

This skill must emit:
- INVALID_ARGUMENT_LAYOUT
- GRID_DIM_MISMATCH
- MISSING_COMPLETION_PATH
- FAULT_CONTRACT_FAIL
- APP_COMPILE_FAIL
- FRONTEND_RUNTIME_MAPPING_MISMATCH
- MEMORY_DUMP_CONTRACT_MISMATCH
- MAGIC_CONSTANT_UNBOUND
- INSUFFICIENT_SKILL_ASSET

## Report Schema

The report must include:
- verdict
- consumed_ir_hash
- produced_ir_hash
- runtime_smoke_trace_hash
- failed_fields
- missing_assets
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- launch_contract.md
- abi_validation.md
- completion_fault_validation.md
- shared/schemas/runtime_validation_report_ir.schema.yaml
- shared/schemas/software_stack_contract_ir.schema.yaml
- shared/schemas/program_image_contract_ir.schema.yaml
- shared/schemas/test_app_contract_ir.schema.yaml
- shared/tables/runtime_smoke_test_table.yaml
- shared/tables/software_stack_contract_table.yaml
- shared/tables/end_to_end_smoke_test_table.yaml

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
