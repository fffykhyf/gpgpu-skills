---
name: gpgpu-rtl
description: Use when SYSTEM_CONTRACT_IR, GOLDEN_CONTRACT_MODEL, and toolchain runtime artifacts must be bound module by module into INCREMENTAL_RTL_MAP with interface contract checking, loader binding, and RTL partial simulation evidence.
---

# GPGPU Incremental RTL Binding Engine

## Role

This skill lowers the system contract into modular RTL bindings. It replaces global RTL-map generation with module-by-module assembly, interface checking, and partial simulation gates.

Rocket lessons are used only for interface negotiation, generated harness
closure, unit-test, monitor, fuzzer, trace sink, and compile-only drift patterns.
Do not copy Rocket scalar pipeline structure or CPU privilege semantics.

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
- `RESOLVED_CONFIG_IR`
- `SYSTEM_COMPOSITION_IR`
- `NEGOTIATED_INTERFACE_IR`
- `ADAPTER_CONTRACT`
- `PROTOCOL_MONITOR_CONTRACT`
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
- `PROTOCOL_MONITOR_CONTRACT`
- `MODULE_INTERFACE_REPORT`
- `RTL_PARTIAL_SIM_REPORT`
- `RTL_MODULE_CONTRACT`
- `RTL_TRACE_CONTRACT`
- `COUNTER_TAP_POINT_PLAN`
- `HARNESS_CLOSURE_REPORT`
- `UNIT_TEST_CONTRACT`
- `SHADOW_MEMORY_CHECKER_PLAN`
- `ADAPTER_FUZZER_PLAN`
- `TRACE_SINK_CONTRACT`
- `COMPILE_ONLY_DRIFT_EVIDENCE`
- `SIMULATOR_ARTIFACT_REJECTION_REPORT`

Human-facing report:
- `IMPLEMENTATION_DASHBOARD.zh.md`

AI-facing artifacts:
- English `INCREMENTAL_RTL_MAP.yaml`
- English `MODULE_INTERFACE_REPORT.yaml`
- English `RTL_PARTIAL_SIM_REPORT.yaml`
- English `PROTOCOL_MONITOR_CONTRACT.yaml`
- English `RTL_MODULE_CONTRACT.md`
- English `RTL_TRACE_CONTRACT.md`
- English `COUNTER_TAP_POINT_PLAN.md`
- English `HARNESS_CLOSURE_REPORT.md`
- English `UNIT_TEST_CONTRACT.md`
- English `SHADOW_MEMORY_CHECKER_PLAN.md`
- English `ADAPTER_FUZZER_PLAN.md`
- English `TRACE_SINK_CONTRACT.md`
- English `COMPILE_ONLY_DRIFT_EVIDENCE.md`
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
- negotiated edge consumption before interface binding
- adapter contract binding for width, fragment, source-id, atomic, and protocol bridge adapters
- protocol monitor instantiation from `PROTOCOL_MONITOR_CONTRACT`
- harness closure for every external port
- unit-test start/finished/timeout contract generation
- shadow memory checker plan binding
- adapter fuzzer plan binding
- trace sink contract binding
- compile-only drift evidence collection for named configs

Required reference lessons:
- `VORTEX_LSU_LANE_FORMAT`
- `VORTEX_NONBLOCKING_MEMORY_TAG`
- `VORTEX_COALESCER_RESPONSE_RESTORE`
- `VORTEX_CACHE_MSHR_RESPONSE_ROUTE`
- `VORTEX_LOCAL_MEMORY_BANK`
- `VORTEX_BARRIER_WSYNC_DRAIN`
- `VORTEX_SIMX_RTL_TWIN`
- `ROCKET_NEGOTIATED_INTERFACE_EDGE`
- `ROCKET_INTERFACE_ADAPTER_CONTRACT`
- `ROCKET_PROTOCOL_MONITOR_CONTRACT`
- `ROCKET_HARNESS_CLOSURE_GATE`
- `ROCKET_COMPILE_ONLY_DRIFT_GATE`

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

## Negotiated Interface Binding Rules

RTL module ports may be bound only from `NEGOTIATED_INTERFACE_IR`,
`ADAPTER_CONTRACT`, and `PROTOCOL_MONITOR_CONTRACT` records. raw wire binding is
forbidden unless it comes from a negotiated edge.

Required binding checks:

- Endpoint widths, source IDs, sink IDs, masks, transfer sizes, and response
  shape come from the negotiated edge.
- Width, fragment, source-id, atomic, and protocol bridge adapters must bind
  the exact `ADAPTER_CONTRACT` state and translated fields.
- Protocol monitors must be instantiated or waived with owner-approved evidence
  before partial simulation can pass.
- Interface checker failures block full-system simulation.

## Generated Verification Closure

Every generated RTL top or unit must provide:

- harness closure for each external DRAM, host, MMIO, debug, trace, interrupt,
  clock, and reset port
- unit-test start/finished/timeout where a block is unit-testable
- protocol monitor evidence for negotiated interfaces
- shadow memory checker evidence for memory or atomic paths
- adapter fuzzer evidence for width, fragment, source-id, atomic, or protocol
  bridge adapters
- trace sink evidence for runtime-visible traces
- compile-only drift evidence for named configs that are not executed

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
- allow raw wire binding without a negotiated edge
- leave a generated harness port dangling

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
- `shared/schemas/system_composition_ir.schema.yaml`
- `shared/schemas/negotiated_interface_ir.schema.yaml`
- `shared/schemas/adapter_contract.schema.yaml`
- `shared/schemas/protocol_monitor_contract.schema.yaml`
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
- Interface binding must consume `NEGOTIATED_INTERFACE_IR` or fail.
- Adapter RTL must consume `ADAPTER_CONTRACT` or fail.
- Protocol monitors must consume `PROTOCOL_MONITOR_CONTRACT` or fail.
- raw wire binding is forbidden unless it comes from a negotiated edge.
- Every generated top proves harness closure for all external ports.
- Every unit-testable block exposes unit-test start/finished/timeout.
- Memory/atomic verification includes a shadow memory checker when memory-visible data can change.
- Every adapter path has an adapter fuzzer plan or an explicit unsupported waiver.
- Runtime-visible trace paths include a trace sink contract.
- Named configs not executed in regression include compile-only drift evidence.
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
- `NEGOTIATED_EDGE_MISSING`
- `ADAPTER_CONTRACT_MISSING`
- `PROTOCOL_MONITOR_MISSING`
- `HARNESS_CLOSURE_FAIL`
- `UNIT_TEST_TIMEOUT_CONTRACT_MISSING`
- `SHADOW_MEMORY_CHECKER_MISSING`
- `ADAPTER_FUZZER_MISSING`
- `TRACE_SINK_UNDECLARED`
- `COMPILE_ONLY_DRIFT_EVIDENCE_MISSING`
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
- negotiated_interface_ir_hash
- adapter_contract_hash
- protocol_monitor_contract_hash
- incremental_rtl_map_hash
- module_results
- interface_results
- partial_sim_results
- timing_feedback_results
- harness_closure_results
- unit_test_contract_results
- adapter_fuzzer_results
- compile_only_drift_results
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
- `shared/schemas/negotiated_interface_ir.schema.yaml`
- `shared/schemas/adapter_contract.schema.yaml`
- `shared/schemas/protocol_monitor_contract.schema.yaml`
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
