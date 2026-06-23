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
- `warp_exec_model.md`
- `sm_instance_layout.md`
- `shared/references/vortex_memory_sync_lessons.yaml`

## Output IR

Produces:
- `INCREMENTAL_RTL_MAP`
- `INTERFACE_BINDING_IR`
- `MODULE_INTERFACE_REPORT`
- `RTL_PARTIAL_SIM_REPORT`
- `RTL_MODULE_CONTRACT`
- `RTL_TRACE_CONTRACT`
- `COUNTER_TAP_POINT_PLAN`
- `SIMULATOR_ARTIFACT_REJECTION_REPORT`

Human-facing report:
- `IMPLEMENTATION_DASHBOARD.zh.md`

AI-facing artifacts:
- English `INCREMENTAL_RTL_MAP.yaml`
- English `MODULE_INTERFACE_REPORT.yaml`
- English `RTL_PARTIAL_SIM_REPORT.yaml`
- English `RTL_MODULE_CONTRACT.md`
- English `RTL_TRACE_CONTRACT.md`
- English `COUNTER_TAP_POINT_PLAN.md`
- English `SIMULATOR_ARTIFACT_REJECTION_REPORT.md`

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
- SM instance layout binding
- warp execution model binding
- EXEC-mask driven SIMD gating checks
- SM_ID routing checks
- RTL contract extraction from simulator evidence
- observable trace contract selection
- counter tap point planning
- hardware-rewritten mechanism checklist
- simulator artifact rejection

Required reference lessons:
- `VORTEX_LSU_LANE_FORMAT`
- `VORTEX_NONBLOCKING_MEMORY_TAG`
- `VORTEX_COALESCER_RESPONSE_RESTORE`
- `VORTEX_CACHE_MSHR_RESPONSE_ROUTE`
- `VORTEX_LOCAL_MEMORY_BANK`
- `VORTEX_BARRIER_WSYNC_DRAIN`
- `VORTEX_SIMX_RTL_TWIN`

## Human and AI Output Policy

`INCREMENTAL_RTL_MAP`, `MODULE_INTERFACE_REPORT`, and
`RTL_PARTIAL_SIM_REPORT` are AI-facing English artifacts. Human-facing output
must be `IMPLEMENTATION_DASHBOARD.zh.md`, written in Chinese and limited to
module binding status, interface status, local partial simulation status,
blocked modules, risks, and next module owner.

Do not expose every module's full YAML by default. Register full binding,
interface, and partial-sim artifacts in `ARTIFACT_MANIFEST_IR` and expand them
only when the user asks, an interface is ambiguous, or a downstream owner needs
exact fields.

## RTL Contract Extraction From Simulator Evidence

Imported mechanisms must be rewritten into hardware contracts before RTL
binding. Scoreboard bitsets, SIMT PC/active-mask/reconvergence state, issue
gate, memory request interface, coalescer output interface, packet interface,
cache status output, and counter tap points may become RTL contracts. C++ queues,
`std::set` scoreboard, BookSim configs, AccelWattch objects, CUDA stream stack,
fixed simulator latencies, SM86 queue depths, and PTX opcode latencies may not.

## Observable Trace Contract

RTL traces must expose cycle, core id, warp id, PC, active mask, issue valid,
non-issue reason, scoreboard collision, selected pipe, memory transaction count,
cache status, ICNT status, L2 queue status, DRAM queue status, and writeback
release when the corresponding subsystem exists.

## Counter Tap Point Contract

Each stable counter must have a producer module, producer event, unit, sample
window, reset rule, stable/debug status, and consumer skill. Counter tap points
are hardware observability hooks; power models and root-cause logic remain in
`gpgpu-simppa`.

## Hardware-Rewritten Mechanism Checklist

Every RTL module derived from simulator evidence must name state owner,
structured interfaces, protocol checks, timing/pipeline boundary, trace fields,
and rejection decisions for simulator-only artifacts.

## Simulator Artifact Rejection Checklist

Emit `SIMULATOR_ARTIFACT_REJECTION_REPORT.md` when imported evidence tries to
introduce CUDA stream stack behavior, fixed latencies, BookSim parameters,
AccelWattch internals, SM86 queue depths, or parser-only variables.

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
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/tables/human_report_template_table.yaml`
- `shared/tables/rtl_module_catalog.yaml`
- `shared/tables/module_interface_contract_table.yaml`
- `shared/tables/rtl_partial_sim_gate_table.yaml`
- `shared/tables/contract_semantics_binding_table.yaml`
- `shared/tables/stall_reason_taxonomy.md`
- `shared/tables/gpgpusim_config_taxonomy_seed.md`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/golden_contract_model.schema.yaml`
- `shared/schemas/toolchain_artifact_ir.schema.yaml`
- `shared/schemas/program_image_ir.schema.yaml`
- `shared/schemas/runtime_launch_ir.schema.yaml`
- `shared/schemas/loader_contract_ir.schema.yaml`
- `shared/schemas/incremental_rtl_map.schema.yaml`
- `shared/schemas/module_interface_report_ir.schema.yaml`
- `shared/schemas/rtl_partial_sim_report_ir.schema.yaml`
- `shared/schemas/issue_nonissue_reason.schema.yaml`
- `shared/schemas/simt_state.schema.yaml`
- `shared/schemas/scoreboard_state.schema.yaml`
- `shared/schemas/warp_memory_transaction.schema.yaml`
- `shared/schemas/cache_request_status.schema.yaml`
- `shared/schemas/noc_packet.schema.yaml`
- `shared/schemas/counter_manifest.schema.yaml`

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
- Multi-SM memory-path and full memory-system bindings must consume `sm_instance_layout.md` and `warp_exec_model.md`.
- Multi-SM memory-path and full memory-system bindings must use warp scheduler + SM issue model instead of warp scheduler, SM scheduler, or generic execution pipeline as the top execution contract.
- Every cross-SM request, response, trace event, and performance event must preserve SM_ID routing.
- No RTL module may share execution state across SMs except through declared memory, atomic, barrier, or fabric contracts.
- Partial simulation compares local behavior against a `GOLDEN_CONTRACT_MODEL` slice.
- RTL must expose issue/non-issue, SIMT, scoreboard, memory transaction, cache, ICNT, L2, DRAM queue, and writeback-release trace fields when implemented.
- RTL must reject simulator-private latencies, queues, CUDA/PTX behavior, BookSim parameters, and AccelWattch internals as direct hardware truth.
- Every stable counter must have a tap point and producer event.

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
- `warp_exec_model.md`
- `sm_instance_layout.md`
- `rtl_contract_extraction_from_simulator_evidence.md`
- `observable_trace_contract.md`
- `counter_tap_point_contract.md`
- `hardware_rewritten_mechanism_checklist.md`
- `simulator_artifact_rejection_checklist.md`
- `shared/schemas/toolchain_artifact_ir.schema.yaml`
- `shared/schemas/program_image_ir.schema.yaml`
- `shared/schemas/runtime_launch_ir.schema.yaml`
- `shared/schemas/loader_contract_ir.schema.yaml`
- `shared/schemas/incremental_rtl_map.schema.yaml`
- `shared/schemas/module_interface_report_ir.schema.yaml`
- `shared/schemas/rtl_partial_sim_report_ir.schema.yaml`
- `shared/schemas/issue_nonissue_reason.schema.yaml`
- `shared/schemas/simt_state.schema.yaml`
- `shared/schemas/scoreboard_state.schema.yaml`
- `shared/schemas/warp_memory_transaction.schema.yaml`
- `shared/schemas/cache_request_status.schema.yaml`
- `shared/schemas/noc_packet.schema.yaml`
- `shared/schemas/counter_manifest.schema.yaml`
- `shared/tables/rtl_module_catalog.yaml`
- `shared/tables/module_interface_contract_table.yaml`
- `shared/tables/rtl_partial_sim_gate_table.yaml`
- `shared/tests/incremental_rtl_binding_engine/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_incremental_rtl_map.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
