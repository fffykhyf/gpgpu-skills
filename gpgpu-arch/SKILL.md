---
name: gpgpu-arch
description: Use when a GPGPU design request, complete spec request, patch request, or trace-driven redesign must become DESIGN_INTENT_IR, candidate ARCH_IR, and MICRO_CONSTRAINT_ESTIMATE_IR before any system contract, golden semantics, RTL binding, performance attribution, or rewrite patch is produced.
---

# GPGPU Architecture Generator

## Role

This skill is the entry generator for the self-correcting GPGPU design system. It classifies the request, locks design intent, constructs candidate architecture graphs, and estimates micro-constraints before any semantic truth or RTL binding is frozen.

## Position in Flow

Upstream:
- user request
- optional complete spec
- optional trace or patch request
- optional reference evidence from `reader`

Downstream:
- `gpgpu-interconnect` for fabric contract fragments when interconnect is enabled
- `gpgpu-memory` for memory-path contract fragments when memory hierarchy is enabled
- `gpgpu-atomic-sync` for atomic, fence, barrier, and WSYNC fragments when synchronization is enabled
- `gpgpu-golden`

## Input IR

Consumes:
- user_request
- optional_spec
- optional_trace
- optional_patch_request
- architecture_preset_library
- hard_constraint_table
- quality_target_table
- requirement_owner_table
- reference_lesson_index

## Output IR

Produces:
- `MODE_SELECTION_IR`
- `DESIGN_INTENT_IR`
- `ARCH_IR`
- `CAPABILITY_PROFILE_IR`
- `MICRO_CONSTRAINT_ESTIMATE_IR`
- `ARCH_GENERATION_REPORT`
- `CONFIG_CLASSIFICATION_TABLE`
- `SM_ISSUE_GATE_CONTRACT`
- `NON_ISSUE_REASON_TAXONOMY`
- `SIMULATOR_ONLY_EXCLUSION_REPORT`

Human-facing reports:
- `DESIGN_BRIEF.zh.md`
- `ARCHITECTURE_DECISION.zh.md`

AI-facing artifacts:
- English `DESIGN_INTENT_IR.yaml`
- English `ARCH_IR.yaml`
- English `MICRO_CONSTRAINT_ESTIMATE_IR.yaml`
- English `ARCH_GENERATION_REPORT.yaml`
- English `ARCH_IR.md`
- English `CONFIG_CLASSIFICATION_TABLE.md`
- English `SM_ISSUE_GATE_CONTRACT.md`
- English `NON_ISSUE_REASON_TAXONOMY.md`
- English `SIMULATOR_ONLY_EXCLUSION_REPORT.md`

## Owned Decisions

This skill owns:
- request classification
- intent locking
- candidate architecture graph construction
- preset selection
- requirement coverage
- micro-constraint estimation
- hard-constraint prefiltering
- candidate risk reporting
- SM-centric hierarchy selection
- warp state contract selection
- CTA/workgroup dispatcher ownership
- warp scheduler policy and fairness caveat
- register-file logical/physical organization
- scoreboard reserve/release policy
- memory coalescer placement and response-shape restoration
- verification backend matrix selection
- capability profile selection
- imported evidence classification before architecture use
- SM issue/non-issue contract selection
- scheduler-visible warp, SIMT, scoreboard, and pipe state contract
- simulator-only architecture artifact rejection
- architecture-level performance attribution order

## Preset Selection Rules

Apply deterministic preset rules before free-form candidate synthesis:

1. If `validation_target` or `prototype_credibility_target` contains all of `compile_kernel_to_program_image`, `rtl_sim_smoke_test`, and `memory_dump_golden_check`, prefer `MINIMAL_VERTICAL_SLICE_GPGPU`.
2. If the user target is teaching only and there is no runtime, frontend, or vertical-slice requirement, prefer `MINIMAL_WARP_SM_TEACHING`.
3. If the request targets `minimal_simt_core`, prefer `MINIMAL_SIMT_CORE`.
4. If the request targets `single_sm_warp_pipeline`, prefer
   `SINGLE_SM_WARP_PIPELINE`.
5. If the request targets `toolchain_runtime_vertical_slice`, prefer
   `TOOLCHAIN_RUNTIME_VERTICAL_SLICE`.
6. If the request targets `multi_sm_memory_path`, prefer
   `MULTI_SM_MEMORY_PATH`.
7. If the request targets `full_memory_sync_system`, prefer
   `FULL_MEMORY_SYNC_SYSTEM`.
8. If the workload needs memory latency hiding or `warp_slots_per_sm > 1`,
   prefer a multi-warp SM preset unless rule 1 already selected the
   vertical-slice preset.

When multiple rules match, use the first applicable rule in `shared/tables/architecture_preset_library.yaml`, record the selected rule, and list lower-priority matching presets in `rejected_alternatives`. If the selected preset fails a hard constraint, emit the failure instead of guessing a replacement.

## Human and AI Output Policy

When `output_mode` is `FAST_ITERATION`, emit only concise Chinese
human-facing summaries by default: `DESIGN_BRIEF.zh.md` and
`ARCHITECTURE_DECISION.zh.md`. Full `DESIGN_INTENT_IR`, `ARCH_IR`, and
`MICRO_CONSTRAINT_ESTIMATE_IR` must still be generated as English AI artifacts
and registered in `ARTIFACT_MANIFEST_IR`.

Do not expose full `ARCH_IR` to the user unless the user explicitly asks for it,
`output_mode` is `CONTRACT_FREEZE`, root cause analysis needs exact affected
architecture paths, or a downstream owner needs exact fields.

## Imported Evidence Classification

Before any mechanism from GPGPU-Sim, Vortex, MIAOW, Rocket, XiangShan, or another
reference can influence `ARCH_IR`, classify it with
`shared/schemas/config_parameter_classification.schema.yaml` and the intake rules
in `imported_evidence_classification.md`. Simulator-private, debug-only, and
parser-only items must not enter hardware contracts.

## SM Issue / Non-Issue Contract

Every generated SM architecture must emit `SM_ISSUE_GATE_CONTRACT.md` and answer:
SM count, warp schedulers per SM, issue width, scoreboard collision checks, SIMT
PC/active-mask ownership, pipe-unavailable attribution, and whether barrier,
membar, atomic, and memory backpressure waits are independent from scoreboard.

## Scheduler-Visible State Contract

Every architecture candidate that can execute warps must expose `warp_state`,
`SIMT_state`, `Scoreboard_state`, and `pipe_state` as scheduler-visible state.
SIMT owns PC, active mask, reconvergence, call depth, and divergence. Scoreboard
owns pending destinations, long-op destinations, reserve/release events, and
collision results.

## Simulator-Only Exclusion Rules

Reject fixed latencies, C++ queues, BookSim parameters, AccelWattch objects,
CUDA stream stack behavior, PTX opcode latency tables, SM86 queue depths, and
parser-only visualizer variables as architecture truth. Emit
`SIMULATOR_ONLY_EXCLUSION_REPORT.md` when such evidence is encountered.

## Architecture-Level Performance Attribution Rules

Performance-driven architecture changes must rule out launch/occupancy,
scheduler non-issue, scoreboard dependency, SIMT divergence, memory formation,
shared bank conflicts, L1/MSHR, ICNT, L2 queues, return path, and scoreboard
release before blaming DRAM or changing topology.

In `DEBUG_REGRESSION`, show only the architecture delta and rejected alternatives
in Chinese, while passing affected `ARCH_IR` paths as English AI artifact refs.

## Forbidden Actions

This skill must not:
- emit `SYSTEM_CONTRACT_IR`
- emit `GOLDEN_CONTRACT_MODEL`
- emit `INCREMENTAL_RTL_MAP`
- emit `PERF_ATTRIBUTION_GRAPH`
- emit `ARCH_REWRITE_PLAN`
- define ISA semantics, memory ordering semantics, launch ABI truth, scheduler semantics, or RTL module interfaces
- treat `MICRO_CONSTRAINT_ESTIMATE_IR` as final PPA truth

## Required Tables

This skill must use:
- `shared/tables/mode_decision_table.yaml`
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/tables/human_report_template_table.yaml`
- `shared/tables/architecture_preset_library.yaml`
- `shared/tables/hard_constraint_table.yaml`
- `shared/tables/quality_target_table.yaml`
- `shared/tables/requirement_owner_table.yaml`
- `shared/tables/micro_constraint_estimator_table.yaml`
- `shared/tables/verification_backend_matrix.yaml`
- `shared/tables/provenance_table.yaml`
- `shared/tables/enum_table.yaml`
- `shared/tables/gpgpusim_config_taxonomy_seed.md`
- `shared/tables/stall_reason_taxonomy.md`

## Required Schemas

This skill must validate:
- `shared/schemas/mode_selection_ir.schema.yaml`
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/design_intent_ir.schema.yaml`
- `shared/schemas/capability_profile_ir.schema.yaml`
- `shared/schemas/arch_ir.schema.yaml`
- `shared/schemas/micro_constraint_estimate_ir.schema.yaml`
- `shared/schemas/arch_generation_report_ir.schema.yaml`
- `shared/schemas/config_parameter_classification.schema.yaml`
- `shared/schemas/config_parameter_taxonomy.schema.yaml`
- `shared/schemas/issue_nonissue_reason.schema.yaml`
- `shared/schemas/simt_state.schema.yaml`
- `shared/schemas/scoreboard_state.schema.yaml`

## Required Invariants

The output must satisfy:
- `ARCH_IR is a candidate graph`
- Every `ARCH_IR.graph_nodes` entry is a structured graph node with `node_id`, `node_type`, `owned_state`, `input_ports`, `output_ports`, `required_contract_paths`, and `scaling_parameters`.
- `MICRO_CONSTRAINT_ESTIMATE_IR is a feasibility estimate`
- `ARCH_IR` must contain `capability_profile`.
- `capability_profile` must be one of `minimal_simt_core`, `single_sm_warp_pipeline`, `toolchain_runtime_vertical_slice`, `multi_sm_memory_path`, or `full_memory_sync_system`.
- Multi-SM memory-path and full memory-system candidates declare SM as the canonical execution island.
- Multi-SM memory-path and full memory-system candidates use warp scheduler + SM issue model instead of a generic execution pipeline as the top execution contract.
- Warp state must include EXEC mask lifecycle, divergence, and reconvergence status when control flow is in scope.
- Memory-capable candidates must include decode-time `MEMORY_BUNDLE`, rule-based coalescer, LDS, LSU front-end, and SM_ID routing hooks.
- Every `ARCH_IR` candidate must include `verification_profile` with simulator, RTL simulation, module-unit, runtime-launch, synthesis-if-FPGA, and PPA-if-performance requirements.
- Every graph node that owns state must declare `state_owner`, `implementation_policy`, `verification_hooks`, and `backend_matrix` fields.
- This skill must not emit system contract truth, golden semantics, RTL bindings, performance attribution, or rewrite patches.
- Every intent requirement has an owner or explicit non-goal.
- Every architecture parameter has allowed provenance.
- Every imported parameter has classification, provenance, exposure policy, and hardware-contract decision.
- No simulator-private parameter may enter `ARCH_IR` as hardware truth.
- CUDA/PTX compatibility fields must be isolated in an optional compatibility profile.
- Every executable SM candidate has warp state, SIMT state, scoreboard state, issue gate, non-issue reason taxonomy, and memory request generation boundary.
- Every non-issued warp must have an attributable `non_issue_reason`.
- Barrier, membar, atomic, SIMT redirect, memory backpressure, and scoreboard waits must remain distinct.
- Area, memory pressure, warp occupancy, register pressure, and bandwidth estimates carry assumptions and bounds.

## Failure Modes

This skill must emit:
- `INSUFFICIENT_REQUEST`
- `UNSUPPORTED_REQUIREMENT`
- `HARD_CONSTRAINT_FAIL`
- `FORBIDDEN_PROVENANCE`
- `UNREALIZABLE_MICRO_CONSTRAINT`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- verdict
- request_hash
- selected_mode
- capability_profile
- design_intent_hash
- arch_ir_hash
- micro_constraint_estimate_hash
- selected_preset
- rejected_alternatives
- known_unrealizable_risks
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `legacy_request_and_candidate_constraints.md`
- `capability_profile_and_preset.md`
- `warp_state_contract.md`
- `sm_hierarchy_model.md`
- `imported_evidence_classification.md`
- `sm_issue_gate_contract_gpgpusim.md`
- `non_issue_reason_taxonomy.md`
- `scheduler_visible_state_contract.md`
- `simulator_only_exclusion_rules.md`
- `architecture_performance_attribution_rules.md`
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/schemas/mode_selection_ir.schema.yaml`
- `shared/schemas/design_intent_ir.schema.yaml`
- `shared/schemas/arch_ir.schema.yaml`
- `shared/schemas/micro_constraint_estimate_ir.schema.yaml`
- `shared/schemas/arch_generation_report_ir.schema.yaml`
- `shared/schemas/config_parameter_classification.schema.yaml`
- `shared/schemas/issue_nonissue_reason.schema.yaml`
- `shared/schemas/simt_state.schema.yaml`
- `shared/schemas/scoreboard_state.schema.yaml`
- `shared/templates/imported_reference_intake.md`
- `shared/templates/config_classification_table.md`
- `shared/templates/sm_issue_gate_contract.md`
- `shared/tables/micro_constraint_estimator_table.yaml`
- `shared/tables/verification_backend_matrix.yaml`
- `shared/tests/architecture_generator/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_arch_ir.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_micro_constraint_estimate.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
