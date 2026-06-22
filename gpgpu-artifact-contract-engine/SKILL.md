---
name: gpgpu-artifact-contract-engine
description: Use when SPEC_IR and GPU_STATE_IR must be mapped to deterministic RTL, simulator, runtime, software stack, memory, config, validation, PPA contracts, and cross-artifact consistency gates.
---

# GPGPU Artifact Contract Engine

## Role

This skill is the deterministic transform and config binding pass. It maps state truth to artifact contracts without making new architecture decisions and emits cross_artifact_consistency_gate plus declared_test_coverage_gate evidence.

## Position in Flow

Upstream:
- gpgpu-spec-lock SPEC_IR
- gpgpu-canonical-state-engine GPU_STATE_IR

Downstream:
- gpgpu-runtime-validator
- gpgpu-memory-subsystem
- gpgpu-implementation-validator
- gpgpu-closure-refinement-engine

## Input IR

Consumes:
- SPEC_IR
- GPU_STATE_IR

## Output IR

Produces:
- RTL_MAPPING_IR
- SIM_BEHAVIOR_IR
- RUNTIME_CONTRACT_IR
- SOFTWARE_STACK_CONTRACT_IR
- PROGRAM_IMAGE_CONTRACT_IR
- TEST_APP_CONTRACT_IR
- MEMORY_MODEL_IR
- CONFIG_BINDING_IR
- VALIDATION_PLAN_IR
- PPA_COUNTER_MAP
- ARTIFACT_CONTRACT_REPORT

## Owned Decisions

This skill owns:
- Deterministic transform
- Config parameter ownership
- Artifact mapping coverage
- Validation plan emission
- PPA counter binding
- cross_artifact_consistency_gate
- declared_test_coverage_gate
- source-of-truth artifact generation mapping

## Forbidden Actions

This skill must not:
- Infer mappings without table entries
- Let runtime or RTL reinterpret ABI fields
- Leak debug-only fields to ABI
- Treat config as independent design truth

## Required Tables

This skill must use:
- shared/tables/artifact_mapping_table.yaml
- shared/tables/config_ownership_table.yaml
- shared/tables/source_of_truth_generation_table.yaml
- shared/tables/cross_artifact_consistency_table.yaml
- shared/tables/software_stack_contract_table.yaml
- shared/tables/end_to_end_smoke_test_table.yaml
- shared/tables/state_to_rtl_mapping.yaml
- shared/tables/state_to_sim_mapping.yaml
- shared/tables/state_to_runtime_mapping.yaml
- shared/tables/state_to_memory_mapping.yaml

## Required Schemas

This skill must validate:
- shared/schemas/rtl_mapping_ir.schema.yaml
- shared/schemas/sim_behavior_ir.schema.yaml
- shared/schemas/runtime_contract_ir.schema.yaml
- shared/schemas/software_stack_contract_ir.schema.yaml
- shared/schemas/program_image_contract_ir.schema.yaml
- shared/schemas/test_app_contract_ir.schema.yaml
- shared/schemas/memory_model_ir.schema.yaml
- shared/schemas/config_binding_ir.schema.yaml
- shared/schemas/validation_plan_ir.schema.yaml

## Required Invariants

The output must satisfy:
- Every consumed state field is mapped or explicit_unused
- Every config parameter has owner and visibility
- ABI fields have one interpretation
- Missing mapping fails closed
- SPEC_IR.isa is byte-or-semantically equivalent to generated RTL/tool/doc opcode artifacts
- Declared validation tests appear in the runner and at least compile/generate

## Failure Modes

This skill must emit:
- MISSING_MAPPING_FAIL_CLOSED
- CONFIG_OWNER_MISSING
- ABI_FIELD_REINTERPRETED
- DEBUG_ONLY_LEAKS_TO_ABI
- DOC_ARTIFACT_DRIFT
- ISA_ENCODING_DRIFT
- DECLARED_TEST_NOT_RUN
- MAGIC_CONSTANT_UNBOUND
- INSUFFICIENT_SKILL_ASSET

## Report Schema

The report must include:
- verdict
- consumed_ir_hash
- produced_ir_hash
- mapping_coverage
- config_ownership
- failed_fields
- missing_assets
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- deterministic_transform.md
- config_binding.md
- artifact_mapping.md
- shared/tables/artifact_mapping_table.yaml
- shared/tables/config_ownership_table.yaml
- shared/tables/source_of_truth_generation_table.yaml
- shared/tables/cross_artifact_consistency_table.yaml
- shared/tables/software_stack_contract_table.yaml
- shared/tables/end_to_end_smoke_test_table.yaml
- shared/tables/state_to_rtl_mapping.yaml
- shared/tables/state_to_sim_mapping.yaml
- shared/tables/state_to_runtime_mapping.yaml
- shared/tables/state_to_memory_mapping.yaml

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
