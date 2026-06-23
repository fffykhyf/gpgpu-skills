---
name: gpgpu-atomic-sync
description: Use when atomic operations, warp/SM/grid barriers, memory fences, ordering scopes, serialization points, or synchronization consistency must be defined or debugged.
---

# GPGPU Atomic and Synchronization Contract Engine

## Role

This skill owns `full_memory_sync_system` atomic, barrier, fence, and WSYNC
consistency semantics. It defines
serialization points, ordering scopes, and hierarchical synchronization behavior
without redefining instruction encoding or cache implementation details.

## Position in Flow

Upstream:
- `gpgpu-arch`
- `gpgpu-interconnect`
- `gpgpu-memory`
- `gpgpu-rtl`

Downstream:
- `gpgpu-golden`
- `gpgpu-simppa`
- `gpgpu-loop`

## Input IR

Consumes:
- `ARCH_IR`
- `CAPABILITY_PROFILE_IR`
- `SM_TO_MEMORY_FABRIC_IR`
- `CACHE_COHERENCE_MODEL`
- memory and atomic traces
- barrier and fence traces
- `shared/references/vortex_memory_sync_lessons.yaml`

## Output IR

Produces:
- `CONTRACT_FRAGMENT_IR`
- `ATOMIC_EXECUTION_MODEL`
- `BARRIER_FENCE_CONTRACT`
- `SYNC_CONSISTENCY_REPORT`

Human-facing report:
- synchronization section in `VALIDATION_DASHBOARD.zh.md`

AI-facing artifacts:
- English `ATOMIC_EXECUTION_MODEL.yaml`
- English `BARRIER_FENCE_CONTRACT.yaml`
- English `SYNC_CONSISTENCY_REPORT.yaml`

## Owned Decisions

This skill owns:
- atomic serialization point
- per-SM atomic ordering
- global atomic consistency model
- warp barrier compatibility for legacy wording
- warp barrier semantics
- SM barrier semantics
- grid barrier semantics
- fence ordering semantics
- synchronization trace classification

Required reference lessons:
- `VORTEX_BARRIER_WSYNC_DRAIN`
- `VORTEX_SIMX_RTL_TWIN`

## Human and AI Output Policy

Atomic and synchronization artifacts are AI-facing English artifacts. Human
output is a concise Chinese status section: atomic verdict, fence verdict,
barrier verdict, affected scope, and required revalidation.

Register full artifacts in `ARTIFACT_MANIFEST_IR`.

## Forbidden Actions

This skill must not:
- define instruction encodings
- define cache replacement policy
- define DRAM scheduling
- treat barriers as generic scheduler stalls
- accept atomic behavior without a serialization point
- hide fence scope or drain rule

## Required Tables

This skill must use:
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/tables/human_report_template_table.yaml`
- `shared/tables/revalidation_routing_table.yaml`
- `shared/tables/root_cause_taxonomy.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/normalized_trace_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- ATOMIC_EXECUTION_MODEL defines atomic serialization point and per-SM atomic ordering
- BARRIER_FENCE_CONTRACT defines hierarchical barrier and fence semantics
- every atomic event has source SM, address, scope, serialization point, and visibility event
- every fence event names drain scope and completion condition
- every barrier event names participant scope and release condition
- AI artifacts are registered in `ARTIFACT_MANIFEST_IR`

## Failure Modes

This skill must emit:
- `ATOMIC_SERIALIZATION_POINT_MISSING`
- `ATOMIC_ORDERING_MISMATCH`
- `FENCE_SCOPE_UNDEFINED`
- `FENCE_DRAIN_INCOMPLETE`
- `BARRIER_SCOPE_MISMATCH`
- `GRID_BARRIER_UNSUPPORTED`
- `SYNC_TRACE_INSUFFICIENT`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- verdict
- system_contract_ir_hash
- cache_coherence_model_hash
- atomic_execution_model_hash
- barrier_fence_contract_hash
- atomic_results
- barrier_results
- fence_results
- affected_sm_ids
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `atomic_execution_model.md`
- `barrier_fence_contract.md`

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
