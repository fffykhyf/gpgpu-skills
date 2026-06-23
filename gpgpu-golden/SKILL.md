---
name: gpgpu-golden
description: Use when candidate ARCH_IR or compatible v4 spec/state artifacts must become SYSTEM_CONTRACT_IR and executable GOLDEN_CONTRACT_MODEL reference semantics for execution, memory, launch, and config behavior.
---

# GPGPU System Contract Golden Engine

## Role

This skill freezes the system contract and derives executable reference semantics from that contract. It is the only semantic truth-definition layer in the self-correcting GPGPU design system.

## Position in Flow

Upstream:
- `gpgpu-arch`
- migrated truth ownership constraints captured in `contract_truth_and_state_model.md`

Downstream:
- `gpgpu-runtime`
- `gpgpu-rtl`
- `gpgpu-interconnect`
- `gpgpu-memory`
- `gpgpu-atomic-sync`
- `gpgpu-simppa`

## Input IR

Consumes:
- `ARCH_IR`
- `DESIGN_INTENT_IR`
- `MICRO_CONSTRAINT_ESTIMATE_IR`
- optional complete human spec
- enum table
- provenance table
- contract semantics binding table

## Output IR

Produces:
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `CONTRACT_SEMANTICS_REPORT`

Human-facing report:
- `CONTRACT_FREEZE_SUMMARY.zh.md`

AI-facing artifacts:
- English `SYSTEM_CONTRACT_IR.yaml`
- English `GOLDEN_CONTRACT_MODEL.yaml`
- English `CONTRACT_SEMANTICS_REPORT.yaml`

## Owned Decisions

This skill owns:
- ISA model definition
- instruction encoding truth for assembler/disassembler derivation
- program image semantic contract
- entry symbol resolution contract
- launch ABI layout truth
- architecture semantic freeze
- execution model definition
- state model definition
- memory model definition
- launch model definition
- system-level interface semantics definition
- config contract definition
- source-of-truth ownership
- executable reference semantics derivation
- golden model coverage checking
- warp-step simulator semantics
- EXEC-mask evolution engine
- SM-parallel execution model
- memory bundle semantic execution

## Human and AI Output Policy

`SYSTEM_CONTRACT_IR` and `GOLDEN_CONTRACT_MODEL` are AI-facing English
artifacts. Human-facing output must be `CONTRACT_FREEZE_SUMMARY.zh.md`, written
in Chinese and focused on what is frozen, what is derived, what is forbidden,
and what requires revalidation.

Do not expose the full `SYSTEM_CONTRACT_IR` by default. Human review must focus
on whether ISA, ABI, memory ordering, launch ABI, interface semantics, and config
ownership are clear enough to freeze. Full IR expansion is allowed during
`CONTRACT_FREEZE`, when the user asks, or when a downstream owner needs exact
fields. The full English contract, golden model, and semantics report must be
registered in `ARTIFACT_MANIFEST_IR`.

## Forbidden Actions

This skill must not:
- create RTL module structure
- generate assembler.py directly
- generate disassembler.py directly
- generate runtime launch files directly
- generate program image files directly
- create performance attribution
- create architecture rewrite patches
- let `GOLDEN_CONTRACT_MODEL` define independent ISA, memory, launch, scheduler, config, or interface truth
- accept hidden defaults or duplicate truth owners

## Required Tables

This skill must use:
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/tables/human_report_template_table.yaml`
- `shared/tables/system_truth_ownership_table.yaml` if present during migration
- `shared/tables/config_ownership_table.yaml`
- `shared/tables/contract_semantics_binding_table.yaml`
- `shared/tables/golden_model_coverage_table.yaml`
- `shared/tables/source_of_truth_generation_table.yaml`
- `shared/tables/provenance_table.yaml`
- `shared/tables/enum_table.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/golden_contract_model.schema.yaml`
- `shared/schemas/contract_semantics_report_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- `SYSTEM_CONTRACT_IR` is the only semantic truth source.
- `SYSTEM_CONTRACT_IR.isa_model` owns ISA opcode and instruction encoding truth.
- `SYSTEM_CONTRACT_IR.launch_model.program_image_format` owns program image layout truth.
- `SYSTEM_CONTRACT_IR.launch_model.argument_buffer_layout` owns runtime argument encoding truth.
- `SYSTEM_CONTRACT_IR.launch_model.loader_contract` owns loader contract truth.
- `SYSTEM_CONTRACT_IR.state_model` is structured with canonical state tables for trace diff.
- `SYSTEM_CONTRACT_IR.interface_semantics_model` owns request/response lifecycle semantics.
- `GOLDEN_CONTRACT_MODEL` is executable reference semantics derived from `SYSTEM_CONTRACT_IR`.
- `GOLDEN_CONTRACT_MODEL` steps warp state with explicit EXEC-mask evolution.
- `GOLDEN_CONTRACT_MODEL` models SM-parallel execution without shared execution state across SMs.
- `GOLDEN_CONTRACT_MODEL` executes decode-time `MEMORY_BUNDLE` semantics before LSU/coalescer effects.
- `GOLDEN_CONTRACT_MODEL` must not define independent ISA, memory, launch, scheduler, config, or interface truth.
- Every executable semantics function maps to a contract path.
- Execution, memory, launch, config, and interface semantics have coverage evidence.
- Feature-gated semantics functions are required only when their contract feature is enabled; disabled features must have executable reject/trap behavior or a documented non-executable reason.
- Unmapped contract paths fail closed.

## Failure Modes

This skill must emit:
- `INSUFFICIENT_CONTRACT`
- `HIDDEN_DEFAULT_REJECT`
- `DUPLICATE_TRUTH_OWNER`
- `FORBIDDEN_GOLDEN_TRUTH`
- `CONTRACT_PATH_UNMAPPED`
- `GOLDEN_MODEL_COVERAGE_FAIL`
- `FEATURE_GATE_COVERAGE_FAIL`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- verdict
- arch_ir_hash
- system_contract_ir_hash
- golden_contract_model_hash
- executable_semantics_coverage
- feature_gate_coverage
- interface_semantics_coverage
- failed_contract_paths
- forbidden_independent_truth_check
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `contract_truth_and_state_model.md`
- `executable_semantics_rules.md`
- `golden_model_coverage_and_report.md`
- `../gpgpu-arch/warp_state_contract.md`
- `../gpgpu-arch/sm_hierarchy_model.md`
- `../gpgpu-runtime/lsu_instruction_bundle.md`
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/golden_contract_model.schema.yaml`
- `shared/schemas/contract_semantics_report_ir.schema.yaml`
- `shared/tables/contract_semantics_binding_table.yaml`
- `shared/tables/golden_model_coverage_table.yaml`
- `shared/tables/config_ownership_table.yaml`
- `shared/tests/system_contract_golden_engine/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_system_contract_ir.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_golden_contract_model.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
