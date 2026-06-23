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
- `gpgpu-golden`
- `gpgpu-interconnect` when L4 multi-SM fabric is in scope

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
- `MICRO_CONSTRAINT_ESTIMATE_IR`
- `ARCH_GENERATION_REPORT`

Human-facing reports:
- `DESIGN_BRIEF.zh.md`
- `ARCHITECTURE_DECISION.zh.md`

AI-facing artifacts:
- English `DESIGN_INTENT_IR.yaml`
- English `ARCH_IR.yaml`
- English `MICRO_CONSTRAINT_ESTIMATE_IR.yaml`
- English `ARCH_GENERATION_REPORT.yaml`

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
- L3/L4 scope classification

## Preset Selection Rules

Apply deterministic preset rules before free-form candidate synthesis:

1. If `validation_target` or `prototype_credibility_target` contains all of `compile_kernel_to_program_image`, `rtl_sim_smoke_test`, and `memory_dump_golden_check`, prefer `MINIMAL_VERTICAL_SLICE_GPGPU`.
2. If the user target is teaching only and there is no runtime, frontend, or vertical-slice requirement, prefer `MINIMAL_WARP_SM_TEACHING`.
3. If the request targets L3 or L4, prefer `MINIMAL_WARP_SM` or
   `MULTI_SM_WARP_GPGPU` before legacy-compatible presets.
4. If the workload needs memory latency hiding or `warp_slots_per_sm > 1`,
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

## Required Schemas

This skill must validate:
- `shared/schemas/mode_selection_ir.schema.yaml`
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/design_intent_ir.schema.yaml`
- `shared/schemas/arch_ir.schema.yaml`
- `shared/schemas/micro_constraint_estimate_ir.schema.yaml`
- `shared/schemas/arch_generation_report_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- `ARCH_IR is a candidate graph`
- Every `ARCH_IR.graph_nodes` entry is a structured graph node with `node_id`, `node_type`, `owned_state`, `input_ports`, `output_ports`, `required_contract_paths`, and `scaling_parameters`.
- `MICRO_CONSTRAINT_ESTIMATE_IR is a feasibility estimate`
- L3/L4 candidates declare SM as the canonical execution island.
- L3/L4 candidates use warp scheduler + SM issue model instead of a generic execution pipeline as the top execution contract.
- Warp state must include EXEC mask lifecycle, divergence, and reconvergence status when control flow is in scope.
- Memory-capable candidates must include decode-time `MEMORY_BUNDLE`, rule-based coalescer, LDS, LSU front-end, and SM_ID routing hooks.
- Every `ARCH_IR` candidate must include `verification_profile` with simulator, RTL simulation, module-unit, runtime-launch, synthesis-if-FPGA, and PPA-if-performance requirements.
- Every graph node that owns state must declare `state_owner`, `implementation_policy`, `verification_hooks`, and `backend_matrix` fields.
- This skill must not emit system contract truth, golden semantics, RTL bindings, performance attribution, or rewrite patches.
- Every intent requirement has an owner or explicit non-goal.
- Every architecture parameter has allowed provenance.
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
- `warp_state_contract.md`
- `sm_hierarchy_model.md`
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/schemas/mode_selection_ir.schema.yaml`
- `shared/schemas/design_intent_ir.schema.yaml`
- `shared/schemas/arch_ir.schema.yaml`
- `shared/schemas/micro_constraint_estimate_ir.schema.yaml`
- `shared/schemas/arch_generation_report_ir.schema.yaml`
- `shared/tables/micro_constraint_estimator_table.yaml`
- `shared/tables/verification_backend_matrix.yaml`
- `shared/tests/architecture_generator/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_arch_ir.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_micro_constraint_estimate.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
