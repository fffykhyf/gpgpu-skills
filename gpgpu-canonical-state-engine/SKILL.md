---
name: gpgpu-canonical-state-engine
description: Use when locked SPEC_IR must become deterministic GPU_STATE_IR or when canonical state invariants, transitions, snapshots, and FSM APIs must be checked.
---

# GPGPU Canonical State Engine

## Role

This skill converts static spec truth into the only execution-state truth consumed by runtime, memory, implementation, and closure passes. It expands SIMT, pipeline, scoreboard, and memory stall state into trace-diffable fields.

## Position in Flow

Upstream:
- gpgpu-spec-lock SPEC_IR

Downstream:
- gpgpu-artifact-contract-engine

## Input IR

Consumes:
- SPEC_IR

## Output IR

Produces:
- GPU_STATE_IR
- STATE_CONSTRUCTION_REPORT

## Owned Decisions

This skill owns:
- Initial state construction
- State transition rule binding
- State invariant checking
- Snapshot schema generation
- Trace-diffable pc_table, exec_mask_table, warp_active, warp_halted, scheduler cursor, scoreboard, simt_stack_state, pipeline_registers, memory_stall_state, and performance counters

## Forbidden Actions

This skill must not:
- Plan architecture
- Evaluate quality
- Select templates
- Absorb candidate-only quality estimates
- Create state fields absent from SPEC_IR
- Modify state for RTL or runtime convenience

## Required Tables

This skill must use:
- shared/tables/initial_state_construction_table.yaml
- shared/tables/state_transition_rule_table.yaml
- shared/tables/state_invariant_table.yaml

## Required Schemas

This skill must validate:
- shared/schemas/spec_ir.schema.yaml
- shared/schemas/gpu_state_ir.schema.yaml

## Required Invariants

The output must satisfy:
- Active mask width equals warp width
- Resident warp slots match SPEC_IR
- Scheduler references valid resident warps
- Scoreboard dependencies reference existing registers and events
- Outstanding memory request tags are unique
- pc_table, exec_mask_table, simt_stack_state, pipeline_registers, and memory_stall_state are present in snapshots

## Failure Modes

This skill must emit:
- STATE_CONSTRUCTION_REJECT
- MISSING_TRANSITION_RULE
- STATE_INVARIANT_FAIL
- INVALID_SCHEDULER_STATE
- INSUFFICIENT_SKILL_ASSET

## Report Schema

The report must include:
- verdict
- consumed_ir_hash
- produced_ir_hash
- initialized_fields
- invariant_results
- failed_fields
- missing_assets
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- gpu_state_ir_contract.md
- state_transition_rules.md
- state_invariants.md
- shared/schemas/gpu_state_ir.schema.yaml
- shared/tables/initial_state_construction_table.yaml
- shared/tables/state_transition_rule_table.yaml
- shared/tables/state_invariant_table.yaml

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
