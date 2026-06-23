---
name: gpgpu-memory
description: Use when DRAM controller behavior, L2/cache hierarchy, cache coherence, cross-SM memory visibility, memory ordering, or shared-memory-system contracts must be defined or validated.
---

# GPGPU Memory System Contract Engine

## Role

This skill owns the `full_memory_sync_system` memory-system contract after requests leave the
interconnect fabric. It defines DRAM scheduling, cache write policy, coherence,
visibility, and memory hierarchy evidence.

## Position in Flow

Upstream:
- `gpgpu-arch`
- `gpgpu-interconnect`
- `gpgpu-rtl`

Downstream:
- `gpgpu-golden`
- `gpgpu-atomic-sync`
- `gpgpu-simppa`
- `gpgpu-loop`

## Input IR

Consumes:
- `ARCH_IR`
- `CAPABILITY_PROFILE_IR`
- `SM_TO_MEMORY_FABRIC_IR`
- memory request traces
- L2/DRAM traces
- coherence requirements
- `shared/references/vortex_memory_sync_lessons.yaml`

## Output IR

Produces:
- `CONTRACT_FRAGMENT_IR`
- `DRAM_CONTROLLER_CONTRACT`
- `CACHE_COHERENCE_MODEL`
- `MEMORY_VISIBILITY_REPORT`
- `DRAM_SCHEDULING_REPORT`

Human-facing report:
- memory-system section in `VALIDATION_DASHBOARD.zh.md`

AI-facing artifacts:
- English `DRAM_CONTROLLER_CONTRACT.yaml`
- English `CACHE_COHERENCE_MODEL.yaml`
- English `MEMORY_VISIBILITY_REPORT.yaml`
- English `DRAM_SCHEDULING_REPORT.yaml`

## Owned Decisions

This skill owns:
- memory request ordering
- DRAM burst scheduling
- bank-level parallelism model
- writeback vs write-through policy
- cross-SM coherence
- atomic visibility rules handoff
- cache line state model
- memory visibility evidence

Required reference lessons:
- `VORTEX_LSU_LANE_FORMAT`
- `VORTEX_NONBLOCKING_MEMORY_TAG`
- `VORTEX_COALESCER_RESPONSE_RESTORE`
- `VORTEX_CACHE_MSHR_RESPONSE_ROUTE`
- `VORTEX_MSHR_DEADLOCK_GUARD`
- `VORTEX_LOCAL_MEMORY_BANK`

## Human and AI Output Policy

Full DRAM and coherence models are AI-facing English artifacts. Human-facing
output is a concise Chinese dashboard: DRAM verdict, coherence verdict, top
bank conflict, affected SM IDs, and revalidation gates.

Register full artifacts in `ARTIFACT_MANIFEST_IR`.

## Forbidden Actions

This skill must not:
- redefine ISA memory instructions
- redefine SM issue readiness
- define atomic serialization point independently from `gpgpu-atomic-sync`
- hide cross-SM visibility in cache implementation details
- treat simulation memory arrays as production cache/DRAM truth

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
- DRAM_CONTROLLER_CONTRACT defines ordering, burst scheduling, and bank-level parallelism model
- CACHE_COHERENCE_MODEL defines writeback vs write-through policy and cross-SM coherence
- cache coherence never changes atomic visibility rules without atomic-sync ownership
- every memory visibility claim cites source SM, address range, request order, and response order
- AI artifacts are registered in `ARTIFACT_MANIFEST_IR`

## Failure Modes

This skill must emit:
- `DRAM_ORDERING_UNDEFINED`
- `DRAM_BANK_MODEL_MISSING`
- `CACHE_POLICY_UNDEFINED`
- `COHERENCE_STATE_MISSING`
- `CROSS_SM_VISIBILITY_MISMATCH`
- `ATOMIC_VISIBILITY_UNBOUND`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- verdict
- system_contract_ir_hash
- fabric_ir_hash
- dram_controller_contract_hash
- cache_coherence_model_hash
- memory_visibility_results
- dram_scheduling_results
- coherence_results
- affected_sm_ids
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `dram_controller_contract.md`
- `cache_coherence_model.md`
- `l1_coalescer_cache_contract.md`
- `mshr_deadlock_guard.md`
- `memory_response_routing.md`

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
