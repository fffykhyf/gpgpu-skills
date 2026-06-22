---
name: gpgpu-front-end
description: Use when a user request, optional spec, optional trace, or patch request must be routed into the GPGPU compiler flow and design intent must be locked without architecture inference.
---

# GPGPU Front End

## Role

This skill is the entry compiler pass. It classifies the request and, for DESIGN mode, locks design intent into a bounded IR before any architecture synthesis occurs.

## Position in Flow

Upstream:
- User Request
- optional_spec
- optional_trace
- optional_patch_request

Downstream:
- gpgpu-architecture-synthesizer for DESIGN
- gpgpu-spec-lock for REPRODUCE
- gpgpu-closure-refinement-engine for TRACE_DEBUG or PATCH_REQUEST

## Input IR

Consumes:
- user_request
- optional_spec
- optional_trace
- optional_patch_request

## Output IR

Produces:
- MODE_SELECTION_IR
- DESIGN_INTENT_IR when mode is DESIGN
- FRONT_END_REPORT

## Owned Decisions

This skill owns:
- Mode classification: REPRODUCE, DESIGN, PATCH_REQUEST, TRACE_DEBUG
- Design intent fields: objective, non-goals, workload, platform, constraints, verification target
- Routing evidence and rejected routes

## Forbidden Actions

This skill must not:
- Choose warp size, SM count, cache policy, scheduler policy, ISA encoding, memory hierarchy, register file size, or RTL pipeline
- Emit SPEC_IR, ARCH_CANDIDATE_IR, or GPU_STATE_IR
- Treat vague goals as complete specs

## Required Tables

This skill must use:
- shared/tables/mode_decision_table.yaml
- shared/tables/enum_table.yaml

## Required Schemas

This skill must validate:
- shared/schemas/mode_selection_ir.schema.yaml
- shared/schemas/design_intent_ir.schema.yaml

## Required Invariants

The output must satisfy:
- Every routed request has exactly one mode
- DESIGN_INTENT_IR contains no architecture parameters
- PATCH_REQUEST and TRACE_DEBUG preserve evidence anchors

## Failure Modes

This skill must emit:
- INSUFFICIENT_REQUEST
- FORBIDDEN_ARCHITECTURE_FIELD
- AMBIGUOUS_MODE
- INSUFFICIENT_SKILL_ASSET

## Report Schema

The report must include:
- verdict
- consumed_ir_hash
- produced_ir_hash
- selected_mode
- failed_fields
- missing_assets
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- mode_selection.md
- design_intent_lock.md
- shared/schemas/mode_selection_ir.schema.yaml
- shared/schemas/design_intent_ir.schema.yaml
- shared/tables/mode_decision_table.yaml
- shared/tests/front_end/cases.yaml

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
