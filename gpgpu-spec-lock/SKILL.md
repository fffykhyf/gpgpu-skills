---
name: gpgpu-spec-lock
description: Use when a human spec or synthesized spec draft must become complete, unambiguous, provenance-bearing SPEC_IR with no hidden defaults.
---

# GPGPU Spec Lock

## Role

This skill locks static architecture facts. It parses and validates, but it does not design missing fields.

## Position in Flow

Upstream:
- Human complete spec
- gpgpu-architecture-synthesizer SYNTHESIZED_SPEC_DRAFT

Downstream:
- gpgpu-canonical-state-engine

## Input IR

Consumes:
- HUMAN_SPEC
- SYNTHESIZED_SPEC_DRAFT
- enum_table
- provenance_table
- spec_required_field_table

## Output IR

Produces:
- SPEC_IR
- SPEC_LOCK_REPORT

## Owned Decisions

This skill owns:
- ISA
- warp model
- thread/block/grid model
- scheduler policy
- register file
- memory hierarchy
- CSR/DCR
- launch ABI
- config defaults
- debug/test hooks

## Forbidden Actions

This skill must not:
- Infer missing warp size, scheduler, memory hierarchy, ISA, or cache policy
- Accept hidden defaults or forbidden provenance
- Emit GPU_STATE_IR
- Pass free-form prose downstream

## Required Tables

This skill must use:
- shared/tables/spec_required_field_table.yaml
- shared/tables/enum_table.yaml
- shared/tables/provenance_table.yaml

## Required Schemas

This skill must validate:
- shared/schemas/spec_ir.schema.yaml
- shared/schemas/synthesized_spec_draft.schema.yaml

## Required Invariants

The output must satisfy:
- No ambiguity
- No hidden default
- All enums resolved
- Every field has provenance
- Field order and hash are stable

## Failure Modes

This skill must emit:
- INSUFFICIENT_SPEC
- HIDDEN_DEFAULT_REJECT
- UNKNOWN_ENUM_REJECT
- FORBIDDEN_PROVENANCE
- CONFLICTING_SPEC_FIELD
- INSUFFICIENT_SKILL_ASSET

## Report Schema

The report must include:
- verdict
- source_kind
- consumed_ir_hash
- produced_ir_hash
- locked_fields
- failed_fields
- missing_assets
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- spec_ir_contract.md
- canonical_serialization.md
- provenance_rules.md
- shared/schemas/spec_ir.schema.yaml
- shared/tables/spec_required_field_table.yaml
- shared/tables/enum_table.yaml
- shared/tables/provenance_table.yaml

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
