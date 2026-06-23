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
- `gpgpu-interconnect`
- `gpgpu-memory`
- `gpgpu-atomic-sync`
- migrated truth ownership constraints captured in `contract_truth_and_state_model.md`

Downstream:
- `gpgpu-runtime`
- `gpgpu-rtl`
- `gpgpu-simppa`

## Input IR

Consumes:
- `ARCH_IR`
- `CONTRACT_FRAGMENT_IR`
- `DESIGN_INTENT_IR`
- `MICRO_CONSTRAINT_ESTIMATE_IR`
- optional complete human spec
- enum table
- provenance table
- contract semantics binding table
- `shared/references/vortex_memory_sync_lessons.yaml`

## Output IR

Produces:
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `CONTRACT_SEMANTICS_REPORT`
- `GOLDEN_FUNCTIONAL_MODEL_SPEC`
- `SIMT_GOLDEN_TRACE_SPEC`
- `MEMORY_TRANSACTION_GOLDEN_SPEC`
- `ATOMIC_FENCE_BARRIER_GOLDEN_SPEC`
- `COMPATIBILITY_PROFILE`

Human-facing report:
- `CONTRACT_FREEZE_SUMMARY.zh.md`

AI-facing artifacts:
- English `SYSTEM_CONTRACT_IR.yaml`
- English `GOLDEN_CONTRACT_MODEL.yaml`
- English `CONTRACT_SEMANTICS_REPORT.yaml`
- English `SYSTEM_CONTRACT_IR.md`
- English `GOLDEN_FUNCTIONAL_MODEL_SPEC.md`
- English `SIMT_GOLDEN_TRACE_SPEC.md`
- English `MEMORY_TRANSACTION_GOLDEN_SPEC.md`
- English `ATOMIC_FENCE_BARRIER_GOLDEN_SPEC.md`
- English `COMPATIBILITY_PROFILE.md`

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
- contract fragment freeze
- module twin model derivation
- functional-vs-timing boundary enforcement
- ISA functional semantics separate from timing stalls
- SIMT functional trace contract
- memory transaction functional contract
- atomic, fence, and barrier golden semantics
- optional CUDA/PTX compatibility profile boundary

Required reference lessons:
- `VORTEX_BARRIER_WSYNC_DRAIN`
- `VORTEX_SIMX_RTL_TWIN`
- `XIANGSHAN_GOLDEN_EXECUTABLE_REF`

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

## Functional vs Timing Boundary

`SYSTEM_CONTRACT_IR` defines functional correctness. Timing stalls, scoreboard
wait cycles, cache latency, ICNT latency, DRAM timing, power, and visualization
counters cannot define ISA, SIMT, memory, launch, fence, atomic, or barrier
semantics. A fence never completes because a simulator waited N cycles; it
completes because its visibility and drain condition is satisfied.

## ISA Functional Semantics

ISA behavior must be project-owned. PTX/CUDA behavior from GPGPU-Sim may only
enter an optional compatibility profile. Native simple-gpgpu opcode effects,
register writes, predicate effects, memory access generation, completion, and
fault behavior must be defined in `SYSTEM_CONTRACT_IR`.

## SIMT Functional Semantics

Golden SIMT behavior must emit PC, active mask, reconvergence PC, call depth,
divergence event, and reconvergence event. SIMT control correctness is checked
independently from scoreboard dependency behavior.

## Memory Transaction Functional Contract

Golden memory semantics must define lane-mask memory behavior and coalescer
input shape through `warp_memory_transaction`. Cache, MSHR, NoC, L2, and DRAM
timing are separate from functional load/store/atomic correctness.

## Atomic / Fence / Barrier Golden Semantics

Atomic, fence, and barrier correctness must be defined by operation type,
return-value behavior, serialization domain, visibility point, completion
condition, participant mask, and release event. GPGPU-Sim atomics/fence notes
are timing-side evidence only; full memory consistency semantics must come from
this project-owned contract or a future deeper `cuda-sim/memory.cc` reader pass.

## Optional CUDA/PTX Compatibility Profile

Compute capability, PTX capability, CUDA stack/heap/sync limits, stream behavior,
texture/constant cache behavior, and PTX-specific atomic/fence semantics must be
isolated in `COMPATIBILITY_PROFILE.md` when selected and excluded otherwise.

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
- `shared/tables/gpgpusim_config_taxonomy_seed.md`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/golden_contract_model.schema.yaml`
- `shared/schemas/contract_semantics_report_ir.schema.yaml`
- `shared/schemas/golden_ref_api.schema.yaml` (`GOLDEN_REF_API`)
- `shared/schemas/architecture_state_blob.schema.yaml` (`ARCHITECTURE_STATE_BLOB`)
- `shared/schemas/golden_sidecar_state.schema.yaml` (`GOLDEN_SIDECAR_STATE`)
- `shared/schemas/store_commit_event.schema.yaml` (`STORE_COMMIT_EVENT`)
- `shared/schemas/golden_status_api.schema.yaml` (`GOLDEN_STATUS_API`)
- `shared/schemas/simt_state.schema.yaml`
- `shared/schemas/warp_memory_transaction.schema.yaml`
- `shared/schemas/atomic_operation.schema.yaml`
- `shared/schemas/fence_visibility.schema.yaml`
- `shared/schemas/barrier_state.schema.yaml`

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
- `GOLDEN_REF_API` exposes a live reference machine with init, memory copy, state copy, event step, event query, and status calls.
- `ARCHITECTURE_STATE_BLOB` contains only diff-visible architectural state.
- `GOLDEN_SIDECAR_STATE` may synchronize and localize debug, but must not define ISA-visible semantics.
- `STORE_COMMIT_EVENT` is required for store mismatch localization.
- `GOLDEN_STATUS_API` separates running, done, faulted, aborted, and timeout states.
- `GOLDEN_CONTRACT_MODEL` steps warp state with explicit EXEC-mask evolution.
- `GOLDEN_CONTRACT_MODEL` models SM-parallel execution without shared execution state across SMs.
- `GOLDEN_CONTRACT_MODEL` executes decode-time `MEMORY_BUNDLE` semantics before LSU/coalescer effects.
- `GOLDEN_CONTRACT_MODEL` must not define independent ISA, memory, launch, scheduler, config, or interface truth.
- Every executable semantics function maps to a contract path.
- Execution, memory, launch, config, and interface semantics have coverage evidence.
- Feature-gated semantics functions are required only when their contract feature is enabled; disabled features must have executable reject/trap behavior or a documented non-executable reason.
- Unmapped contract paths fail closed.
- Functional correctness and timing attribution are separate planes.
- Timing stalls must not define functional semantics.
- SIMT state and scoreboard state must be independently checkable.
- Memory transaction golden tests must cover lane masks and coalescer input.
- Atomic return-value, fence ordering, and CTA barrier release tests are required when synchronization is enabled.
- CUDA/PTX compatibility semantics are optional profile semantics, not native truth.

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
- `functional_timing_boundary.md`
- `simt_golden_trace_spec.md`
- `memory_transaction_golden_spec.md`
- `atomic_fence_barrier_golden_spec.md`
- `compatibility_profile_contract.md`
- `../gpgpu-arch/warp_state_contract.md`
- `../gpgpu-arch/sm_hierarchy_model.md`
- `../gpgpu-runtime/lsu_instruction_bundle.md`
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/golden_contract_model.schema.yaml`
- `shared/schemas/contract_semantics_report_ir.schema.yaml`
- `shared/schemas/simt_state.schema.yaml`
- `shared/schemas/warp_memory_transaction.schema.yaml`
- `shared/schemas/atomic_operation.schema.yaml`
- `shared/schemas/fence_visibility.schema.yaml`
- `shared/schemas/barrier_state.schema.yaml`
- `shared/tables/contract_semantics_binding_table.yaml`
- `shared/tables/golden_model_coverage_table.yaml`
- `shared/tables/config_ownership_table.yaml`
- `shared/tests/system_contract_golden_engine/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_system_contract_ir.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_golden_contract_model.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
