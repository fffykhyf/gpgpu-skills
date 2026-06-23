---
name: gpgpu-rtl
description: Use when SYSTEM_CONTRACT_IR, GOLDEN_CONTRACT_MODEL, and toolchain runtime artifacts must be bound module by module into INCREMENTAL_RTL_MAP with interface contract checking, loader binding, and RTL partial simulation evidence.
---

# GPGPU Incremental RTL Binding Engine

## Role

This skill lowers the system contract into modular RTL bindings. It replaces global RTL-map generation with module-by-module assembly, interface checking, and partial simulation gates.

## Position in Flow

Upstream:
- `gpgpu-golden`
- `gpgpu-runtime`

Downstream:
- `gpgpu-simppa`
- `gpgpu-loop`

## Input IR

Consumes:
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `TOOLCHAIN_ARTIFACT_IR`
- `PROGRAM_IMAGE_IR`
- `RUNTIME_LAUNCH_IR`
- `LOADER_CONTRACT_IR`
- module catalog
- module interface contract table
- RTL partial simulation gate table
- target platform constraints

## Output IR

Produces:
- `INCREMENTAL_RTL_MAP`
- `INTERFACE_BINDING_IR`
- `MODULE_INTERFACE_REPORT`
- `RTL_PARTIAL_SIM_REPORT`

## Owned Decisions

This skill owns:
- module-by-module RTL binding
- program image loader interface binding
- instruction memory initialization binding
- runtime argument buffer interface binding
- module binding template selection
- Interface Contract Checker
- RTL Partial Simulator
- module interface declaration
- structured interface binding IR
- signal consistency checking
- handshake protocol checking
- no-combinational-ready-loop checking
- latency compatibility checking
- pipeline boundary checking
- local timing and synthesis feedback hooks
- partial simulation gate generation
- local trace schema binding

## Forbidden Actions

This skill must not:
- redefine system contract semantics
- create golden semantics
- create performance attribution
- produce architecture rewrite patches
- silently join incompatible module interfaces
- allow global RTL binding without module evidence

## Required Tables

This skill must use:
- `shared/tables/rtl_module_catalog.yaml`
- `shared/tables/module_interface_contract_table.yaml`
- `shared/tables/rtl_partial_sim_gate_table.yaml`
- `shared/tables/contract_semantics_binding_table.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/golden_contract_model.schema.yaml`
- `shared/schemas/toolchain_artifact_ir.schema.yaml`
- `shared/schemas/program_image_ir.schema.yaml`
- `shared/schemas/runtime_launch_ir.schema.yaml`
- `shared/schemas/loader_contract_ir.schema.yaml`
- `shared/schemas/incremental_rtl_map.schema.yaml`
- `shared/schemas/module_interface_report_ir.schema.yaml`
- `shared/schemas/rtl_partial_sim_report_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- `INCREMENTAL_RTL_MAP` binds modules one by one.
- Program image loading must consume `PROGRAM_IMAGE_IR` and `LOADER_CONTRACT_IR`.
- Runtime CSR binding must consume `RUNTIME_LAUNCH_IR`.
- Entry PC fetch must match `PROGRAM_IMAGE_IR.entry_pc`.
- Argument buffer visibility must match `RUNTIME_LAUNCH_IR.arg_buffer_bytes`.
- Every module must reference a `MODULE_BINDING_TEMPLATE`.
- Every module must declare consumed contract paths, required local state, input/output interfaces, latency contract, local trace schema, partial simulation evidence, and timing feedback.
- Every interface must be represented as structured `INTERFACE_BINDING_IR`.
- Every module references `SYSTEM_CONTRACT_IR` paths.
- Interface mismatch prevents full-system simulation.
- Valid/ready and request/response interfaces must prove `no_combinational_ready_loop`.
- Memory path modules must decompose load/store queue, coalescer, shared memory bank unit, L1/global adapter, response router, and fault/completion responsibilities unless an explicit template declares a checked fusion.
- Partial simulation compares local behavior against a `GOLDEN_CONTRACT_MODEL` slice.

## Failure Modes

This skill must emit:
- `MODULE_BINDING_MISSING`
- `INTERFACE_PROTOCOL_MISMATCH`
- `LATENCY_INCOMPATIBLE`
- `PIPELINE_BOUNDARY_FAIL`
- `PARTIAL_SIM_FAIL`
- `CONTRACT_PATH_UNBOUND`
- `MODULE_TEMPLATE_MISSING`
- `PROGRAM_IMAGE_LOAD_FAIL`
- `ENTRY_PC_FETCH_FAIL`
- `ARG_BUFFER_VISIBILITY_FAIL`
- `FIRST_INSTRUCTION_DECODE_FAIL`
- `TAG_REUSE_BEFORE_RESPONSE`
- `PAYLOAD_STABILITY_FAIL`
- `COMBINATIONAL_READY_LOOP`
- `TIMING_FEEDBACK_MISSING`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- verdict
- system_contract_ir_hash
- golden_contract_model_hash
- toolchain_artifact_ir_hash
- program_image_ir_hash
- runtime_launch_ir_hash
- loader_contract_ir_hash
- incremental_rtl_map_hash
- module_results
- interface_results
- partial_sim_results
- timing_feedback_results
- unresolved_binding_risks
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `module_binding_rules.md`
- `interface_binding_and_checker.md`
- `partial_simulation_gates.md`
- `rtl_module_catalog.md`
- `shared/schemas/toolchain_artifact_ir.schema.yaml`
- `shared/schemas/program_image_ir.schema.yaml`
- `shared/schemas/runtime_launch_ir.schema.yaml`
- `shared/schemas/loader_contract_ir.schema.yaml`
- `shared/schemas/incremental_rtl_map.schema.yaml`
- `shared/schemas/module_interface_report_ir.schema.yaml`
- `shared/schemas/rtl_partial_sim_report_ir.schema.yaml`
- `shared/tables/rtl_module_catalog.yaml`
- `shared/tables/module_interface_contract_table.yaml`
- `shared/tables/rtl_partial_sim_gate_table.yaml`
- `shared/tests/incremental_rtl_binding_engine/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_incremental_rtl_map.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
