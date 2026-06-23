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
- `ATOMIC_OPERATION_SPEC`
- `FENCE_VISIBILITY_SPEC`
- `CTA_BARRIER_SPEC`
- `MEMORY_CONSISTENCY_LITMUS`
- `SYNC_STALL_COUNTER_SPEC`

Human-facing report:
- synchronization section in `VALIDATION_DASHBOARD.zh.md`

AI-facing artifacts:
- English `ATOMIC_EXECUTION_MODEL.yaml`
- English `BARRIER_FENCE_CONTRACT.yaml`
- English `SYNC_CONSISTENCY_REPORT.yaml`
- English `ATOMIC_OPERATION_SPEC.md`
- English `FENCE_VISIBILITY_SPEC.md`
- English `CTA_BARRIER_SPEC.md`
- English `MEMORY_CONSISTENCY_LITMUS.md`
- English `SYNC_STALL_COUNTER_SPEC.md`

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
- atomic operation contract
- fence scope and visibility contract
- CTA barrier contract
- memory ordering litmus test selection
- synchronization stall attribution

Required reference lessons:
- `VORTEX_BARRIER_WSYNC_DRAIN`
- `VORTEX_SIMX_RTL_TWIN`

## Human and AI Output Policy

Atomic and synchronization artifacts are AI-facing English artifacts. Human
output is a concise Chinese status section: atomic verdict, fence verdict,
barrier verdict, affected scope, and required revalidation.

Register full artifacts in `ARTIFACT_MANIFEST_IR`.

## Atomic Operation Contract

Atomic operations must define operation type, address, lane mask, byte mask,
return-value behavior, destination register if any, completion event,
serialization domain, and scoreboard release condition. Atomic requests must
state when they issue and when a waiting warp may resume.

## Fence Scope / Visibility Contract

Fence contracts must define scope, ordering domain, affected memory spaces,
visibility point, completion condition, cache flush or invalidate policy, and
stall reason. A fence cannot complete because of a fixed timing delay.

## CTA Barrier Contract

CTA barriers must define CTA id, expected participant count, arrival mask,
release condition, waiting warp list, and release event. Barrier wait is not a
generic scheduler stall.

## Memory Ordering Litmus Tests

Synchronization contracts must include litmus tests for same-address atomic
serialization, atomic return value, fence visibility, CTA barrier release,
store/fence/load ordering, and scoreboard release after atomic or load
completion.

## Synchronization Stall Attribution

Stable synchronization reasons are `atomic_wait`, `atomic_split_or_replay`,
`membar_wait`, `fence_flush_or_invalidate`, and `barrier_wait`. Each reason
requires a synchronization contract event and release condition.

GPGPU-Sim atomics/fence notes only provide timing-side reference. Full memory
consistency semantics must be defined in our own golden contract or by a future
deeper `cuda-sim/memory.cc` reader pass.

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
- `shared/tables/stall_reason_taxonomy.md`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/atomic_operation.schema.yaml`
- `shared/schemas/fence_visibility.schema.yaml`
- `shared/schemas/barrier_state.schema.yaml`

## Required Invariants

The output must satisfy:
- ATOMIC_EXECUTION_MODEL defines atomic serialization point and per-SM atomic ordering
- BARRIER_FENCE_CONTRACT defines hierarchical barrier and fence semantics
- every atomic event has source SM, address, scope, serialization point, and visibility event
- every fence event names drain scope and completion condition
- every barrier event names participant scope and release condition
- atomic_wait, atomic_split_or_replay, membar_wait, fence_flush_or_invalidate, and barrier_wait must be separately attributable.
- atomic requests must define lane participation, return value behavior, destination register, completion event, serialization domain, and scoreboard release.
- fence visibility must define scope, ordering domain, affected spaces, visibility point, completion condition, and cache policy.
- barrier release must define participant mask and release condition.
- GPGPU-Sim timing-side atomic/fence evidence is insufficient as a full memory consistency model.
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
- `atomic_operation_contract.md`
- `fence_scope_visibility_contract.md`
- `cta_barrier_contract.md`
- `memory_ordering_litmus_tests.md`
- `synchronization_stall_attribution.md`
- `shared/schemas/atomic_operation.schema.yaml`
- `shared/schemas/fence_visibility.schema.yaml`
- `shared/schemas/barrier_state.schema.yaml`

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
