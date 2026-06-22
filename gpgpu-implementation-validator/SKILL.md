---
name: gpgpu-implementation-validator
description: Use when RTL SIMT core and golden simulator traces must be validated against GPU_STATE_IR, mapping contracts, memory subsystem behavior, and validation plans.
---

# GPGPU Implementation Validator

## Role

This skill validates RTL and golden simulator behavior against canonical state. It merges the former RTL SIMT core and golden sim responsibilities.

## Position in Flow

Upstream:
- gpgpu-canonical-state-engine GPU_STATE_IR
- gpgpu-artifact-contract-engine RTL_MAPPING_IR, SIM_BEHAVIOR_IR, VALIDATION_PLAN_IR
- gpgpu-memory-subsystem MEMORY_SUBSYSTEM_IR

Downstream:
- gpgpu-closure-refinement-engine

## Input IR

Consumes:
- GPU_STATE_IR
- RTL_MAPPING_IR
- SIM_BEHAVIOR_IR
- MEMORY_SUBSYSTEM_IR
- VALIDATION_PLAN_IR
- trace

## Output IR

Produces:
- IMPLEMENTATION_VALIDATION_REPORT_IR
- RTL_VALIDATION_REPORT
- GOLDEN_SIM_REPORT
- FIRST_DIVERGENCE_REPORT

## Owned Decisions

This skill owns:
- RTL SIMT core validation
- Golden simulator validation
- RTL-vs-golden first divergence
- Trace event consistency

## Forbidden Actions

This skill must not:
- Redefine ISA
- Change GPU_STATE_IR to match RTL
- Let golden sim become a second truth source
- Ignore first divergence evidence

## Required Tables

This skill must use:
- shared/tables/rtl_validation_gate_table.yaml
- shared/tables/golden_sim_trace_field_table.yaml
- shared/tables/first_divergence_taxonomy.yaml

## Required Schemas

This skill must validate:
- shared/schemas/implementation_validation_report_ir.schema.yaml
- shared/schemas/first_divergence_report_ir.schema.yaml

## Required Invariants

The output must satisfy:
- Fetch/decode/issue/execute/writeback obey mapped state
- Active mask updates match transition rules
- Scoreboard stalls and wakeups match memory subsystem contract
- Trace fields cover mandatory semantic fields

## Failure Modes

This skill must emit:
- RTL_VALIDATION_FAIL
- GOLDEN_SIM_REDEFINES_ISA
- FIRST_DIVERGENCE_DETECTED
- TRACE_FIELD_MISSING
- INSUFFICIENT_SKILL_ASSET

## Report Schema

The report must include:
- verdict
- consumed_ir_hash
- produced_ir_hash
- rtl_report_hash
- golden_report_hash
- first_divergence
- failed_fields
- missing_assets
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- rtl_simt_core_validation.md
- golden_sim_validation.md
- first_divergence.md
- shared/schemas/implementation_validation_report_ir.schema.yaml
- shared/schemas/first_divergence_report_ir.schema.yaml
- shared/tables/rtl_validation_gate_table.yaml
- shared/tables/golden_sim_trace_field_table.yaml
- shared/tables/first_divergence_taxonomy.yaml

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
