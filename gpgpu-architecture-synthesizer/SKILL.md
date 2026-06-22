---
name: gpgpu-architecture-synthesizer
description: Use when DESIGN_INTENT_IR must be converted into a bounded architecture candidate using preset tables, hard constraints, scoring rules, and provenance.
---

# GPGPU Architecture Synthesizer

## Role

This skill creates architecture candidates only. It never creates final spec truth and must route every candidate through gpgpu-spec-lock.

## Position in Flow

Upstream:
- gpgpu-front-end DESIGN_INTENT_IR

Downstream:
- gpgpu-spec-lock consumes SYNTHESIZED_SPEC_DRAFT

## Input IR

Consumes:
- DESIGN_INTENT_IR
- architecture_preset_library
- hard_constraint_table
- quality_target_table
- requirement_owner_table

## Output IR

Produces:
- ARCH_CANDIDATE_IR
- SYNTHESIZED_SPEC_DRAFT
- ARCH_SYNTHESIS_REPORT

## Owned Decisions

This skill owns:
- Requirement coverage
- Preset selection
- Parameter allocation
- Hard constraint checking
- Candidate scoring

## Forbidden Actions

This skill must not:
- Emit SPEC_IR or GPU_STATE_IR
- Bypass gpgpu-spec-lock
- Invent topology outside shared/tables/architecture_preset_library.yaml
- Use COMMON_GPU_DEFAULT, MODEL_GUESS, UNKNOWN, or IMPLICIT_DEFAULT provenance

## Required Tables

This skill must use:
- shared/tables/architecture_preset_library.yaml
- shared/tables/hard_constraint_table.yaml
- shared/tables/quality_target_table.yaml
- shared/tables/requirement_owner_table.yaml
- shared/tables/enum_table.yaml
- shared/tables/provenance_table.yaml

## Required Schemas

This skill must validate:
- shared/schemas/design_intent_ir.schema.yaml
- shared/schemas/arch_candidate_ir.schema.yaml
- shared/schemas/synthesized_spec_draft.schema.yaml

## Required Invariants

The output must satisfy:
- ARCH_CANDIDATE_IR != SPEC_IR
- Every intent requirement has an owner or explicit non-goal
- Hard constraints pass before scoring
- Every generated parameter has allowed provenance

## Failure Modes

This skill must emit:
- REJECTED_ARCH_CANDIDATE
- UNSUPPORTED_REQUIREMENT
- HARD_CONSTRAINT_FAIL
- FORBIDDEN_PROVENANCE
- INSUFFICIENT_SKILL_ASSET

## Report Schema

The report must include:
- verdict
- candidate_id
- consumed_ir_hash
- produced_ir_hash
- selected_preset
- constraint_proof
- failed_fields
- missing_assets
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- preset_selection.md
- parameter_allocation.md
- candidate_scoring.md
- shared/schemas/arch_candidate_ir.schema.yaml
- shared/schemas/synthesized_spec_draft.schema.yaml
- shared/tables/architecture_preset_library.yaml
- shared/tables/hard_constraint_table.yaml
- shared/tables/quality_target_table.yaml
- shared/tables/requirement_owner_table.yaml

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
