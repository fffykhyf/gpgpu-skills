---
name: gpgpu-runtime
description: Use when SYSTEM_CONTRACT_IR and GOLDEN_CONTRACT_MODEL must derive assembler, disassembler, ISA tables, assembly IR, program image, runtime launch, loader contract, and toolchain smoke reports without defining independent ISA or ABI truth.
---

# GPGPU Toolchain Runtime Artifact Engine

## Role

This skill derives toolchain and runtime artifacts from `SYSTEM_CONTRACT_IR`. It must not define independent ISA, ABI, program image, loader, or runtime truth.

## Position in Flow

Upstream:
- `gpgpu-golden`

Downstream:
- `gpgpu-rtl`
- `gpgpu-interconnect`
- `gpgpu-memory`
- `gpgpu-atomic-sync`
- `gpgpu-simppa`
- `gpgpu-loop`

## Input IR

Consumes:
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `source_of_truth_generation_table`
- `toolchain_artifact_generation_table`
- `program_image_format_table`
- `runtime_launch_binding_table`
- `loader_contract_table`
- `toolchain_validation_gate_table`

## Output IR

Produces:
- `TOOLCHAIN_ARTIFACT_IR`
- `ASSEMBLY_IR`
- `PROGRAM_IMAGE_IR`
- `RUNTIME_LAUNCH_IR`
- `LOADER_CONTRACT_IR`
- `ASSEMBLER_BINDING_REPORT`
- `TOOLCHAIN_SMOKE_REPORT`

Human-facing output:
- toolchain/runtime section in `VALIDATION_DASHBOARD.zh.md`
- `PATCH_CARD.zh.md` when toolchain or runtime evidence fails

AI-facing artifacts:
- English `TOOLCHAIN_ARTIFACT_IR.yaml`
- English `ASSEMBLY_IR.yaml`
- English `PROGRAM_IMAGE_IR.yaml`
- English `RUNTIME_LAUNCH_IR.yaml`
- English `LOADER_CONTRACT_IR.yaml`
- English `TOOLCHAIN_SMOKE_REPORT.yaml`

## Owned Decisions

This skill owns:
- deterministic derivation of `tools/isa.py`
- deterministic derivation of `tools/encoding_table.py`
- deterministic derivation of `tools/assembler.py`
- deterministic derivation of `tools/disassembler.py`
- deterministic derivation of `tools/program_image.py`
- deterministic derivation of `tools/runtime_launch.py`
- deterministic derivation of `tools/loader.py`
- deterministic derivation of `docs/isa.md`
- deterministic derivation of `docs/program_image_format.md`
- decode-stage `MEMORY_BUNDLE` derivation
- rule-based memory coalescing contract generation
- assembly IR validation
- assembler/disassembler round-trip validation
- program image layout validation
- runtime argument encoding validation
- loader contract validation
- golden program-image execution smoke validation
- source-of-truth hash and semantic equivalence checks

## Human and AI Output Policy

Assembler, disassembler, program image, runtime launch, and loader artifacts are
AI-facing English artifacts. Human-facing output must show only concise Chinese
status fields:

- assembler roundtrip status
- program image hash
- entry PC
- arg buffer hash
- loader memory init hash
- smoke verdict

Do not expose full `ASSEMBLY_IR`, `PROGRAM_IMAGE_IR`, `RUNTIME_LAUNCH_IR`, or
`LOADER_CONTRACT_IR` by default. On toolchain or runtime failure, emit
`PATCH_CARD.zh.md` with the failed gate, evidence summary, owner, and required
revalidation while retaining full English artifacts in `ARTIFACT_MANIFEST_IR`.

## Forbidden Actions

This skill must not:
- define opcode, funct, field, width, signedness, or decode-class truth outside `SYSTEM_CONTRACT_IR.isa_model`
- define launch ABI, argument buffer, entry symbol, or completion truth outside `SYSTEM_CONTRACT_IR.launch_model`
- define program image or loader truth outside `SYSTEM_CONTRACT_IR.launch_model.program_image_format` and `SYSTEM_CONTRACT_IR.launch_model.loader_contract`
- accept hand-written assembler opcode constants
- accept hand-written disassembler opcode constants
- accept RTL defines that drift from `SYSTEM_CONTRACT_IR`
- accept docs as a truth source
- generate RTL module bindings
- generate architecture rewrite patches

## Required Tables

This skill must use:
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/tables/human_report_template_table.yaml`
- `shared/tables/source_of_truth_generation_table.yaml`
- `shared/tables/toolchain_artifact_generation_table.yaml`
- `shared/tables/assembly_syntax_table.yaml`
- `shared/tables/instruction_encoding_derivation_table.yaml`
- `shared/tables/program_image_format_table.yaml`
- `shared/tables/runtime_launch_binding_table.yaml`
- `shared/tables/loader_contract_table.yaml`
- `shared/tables/toolchain_validation_gate_table.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/golden_contract_model.schema.yaml`
- `shared/schemas/toolchain_artifact_ir.schema.yaml`
- `shared/schemas/assembly_ir.schema.yaml`
- `shared/schemas/program_image_ir.schema.yaml`
- `shared/schemas/runtime_launch_ir.schema.yaml`
- `shared/schemas/loader_contract_ir.schema.yaml`
- `shared/schemas/assembler_binding_report_ir.schema.yaml`
- `shared/schemas/toolchain_smoke_report_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- `SYSTEM_CONTRACT_IR` remains the only source of ISA, launch ABI, program image, and loader truth.
- `isa_model_hash == tools_isa_table_hash == assembler_table_hash == disassembler_table_hash == rtl_defines_hash`.
- `ASSEMBLY_IR.contract_hash` matches `SYSTEM_CONTRACT_IR.canonical_hash`.
- `PROGRAM_IMAGE_IR.metadata.isa_model_hash` matches the derived ISA table hash.
- `RUNTIME_LAUNCH_IR.launch_abi` derives from `SYSTEM_CONTRACT_IR.launch_model.abi`.
- `LOADER_CONTRACT_IR` derives from `SYSTEM_CONTRACT_IR.launch_model.loader_contract`.
- Golden execution must consume `PROGRAM_IMAGE_IR`, decode instruction bytes, and emit expected trace or memory dump.
- Memory instructions must emit `MEMORY_BUNDLE` before LSU issue.
- `MEMORY_BUNDLE` must contain address vector, lane mask, access type, memory space, byte enables, ordering scope, and coalescing policy reference.
- Coalescing must be rule-based, including contiguous-address merge, aligned single transaction, bank-conflict split, and divergence fallback.

## Failure Modes

This skill must emit:
- `TOOLCHAIN_ARTIFACT_MISSING`
- `ISA_TABLE_DERIVATION_FAIL`
- `ISA_ENCODING_DRIFT`
- `ASM_PARSE_FAIL`
- `ASM_ENCODE_FAIL`
- `DISASM_DECODE_FAIL`
- `DISASM_ROUNDTRIP_FAIL`
- `UNSUPPORTED_INSTRUCTION_BEHAVIOR_MISMATCH`
- `PROGRAM_IMAGE_LAYOUT_FAIL`
- `ENTRY_SYMBOL_RESOLVE_FAIL`
- `RUNTIME_ARG_ENCODING_FAIL`
- `LOADER_CONTRACT_FAIL`
- `GOLDEN_IMAGE_EXECUTION_FAIL`
- `SOURCE_OF_TRUTH_DRIFT`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- verdict
- system_contract_ir_hash
- golden_contract_model_hash
- toolchain_artifact_ir_hash
- assembly_ir_hash
- program_image_ir_hash
- runtime_launch_ir_hash
- loader_contract_ir_hash
- source_of_truth_checks
- assembler_binding_results
- disassembler_roundtrip_results
- program_image_layout_results
- runtime_launch_results
- loader_contract_results
- golden_image_execution_results
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `isa_table_derivation.md`
- `assembly_ir_rules.md`
- `assembler_disassembler_roundtrip.md`
- `program_image_and_loader_contract.md`
- `runtime_launch_artifact_rules.md`
- `toolchain_smoke_gates.md`
- `memory_coalescing_contract.md`
- `lsu_instruction_bundle.md`
- `shared/schemas/toolchain_artifact_ir.schema.yaml`
- `shared/schemas/assembly_ir.schema.yaml`
- `shared/schemas/program_image_ir.schema.yaml`
- `shared/schemas/runtime_launch_ir.schema.yaml`
- `shared/schemas/loader_contract_ir.schema.yaml`
- `shared/schemas/assembler_binding_report_ir.schema.yaml`
- `shared/schemas/toolchain_smoke_report_ir.schema.yaml`
- `shared/tables/toolchain_artifact_generation_table.yaml`
- `shared/tables/assembly_syntax_table.yaml`
- `shared/tables/instruction_encoding_derivation_table.yaml`
- `shared/tables/program_image_format_table.yaml`
- `shared/tables/runtime_launch_binding_table.yaml`
- `shared/tables/loader_contract_table.yaml`
- `shared/tables/toolchain_validation_gate_table.yaml`
- `shared/tests/toolchain_runtime_artifact_engine/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_toolchain_artifact_ir.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
