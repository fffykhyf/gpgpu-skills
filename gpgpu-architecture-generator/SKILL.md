---
name: gpgpu-architecture-generator
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
- `gpgpu-system-contract-golden-engine`

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
- `shared/tables/architecture_preset_library.yaml`
- `shared/tables/hard_constraint_table.yaml`
- `shared/tables/quality_target_table.yaml`
- `shared/tables/requirement_owner_table.yaml`
- `shared/tables/micro_constraint_estimator_table.yaml`
- `shared/tables/provenance_table.yaml`
- `shared/tables/enum_table.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/mode_selection_ir.schema.yaml`
- `shared/schemas/design_intent_ir.schema.yaml`
- `shared/schemas/arch_ir.schema.yaml`
- `shared/schemas/micro_constraint_estimate_ir.schema.yaml`
- `shared/schemas/arch_generation_report_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- `ARCH_IR is a candidate graph`
- `MICRO_CONSTRAINT_ESTIMATE_IR is a feasibility estimate`
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
- `shared/schemas/mode_selection_ir.schema.yaml`
- `shared/schemas/design_intent_ir.schema.yaml`
- `shared/schemas/arch_ir.schema.yaml`
- `shared/schemas/micro_constraint_estimate_ir.schema.yaml`
- `shared/schemas/arch_generation_report_ir.schema.yaml`
- `shared/tables/micro_constraint_estimator_table.yaml`
- `shared/tests/architecture_generator/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_arch_ir.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_micro_constraint_estimate.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
