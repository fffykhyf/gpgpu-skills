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
- `WARP_MEMORY_TRANSACTION_SPEC`
- `COALESCER_SPEC`
- `SHARED_MEMORY_BANK_CONFLICT_SPEC`
- `L1_CACHE_STATUS_SPEC`
- `MSHR_RESERVATION_FAIL_SPEC`
- `MEMORY_RETURN_PATH_SPEC`

Human-facing report:
- memory-system section in `VALIDATION_DASHBOARD.zh.md`

AI-facing artifacts:
- English `DRAM_CONTROLLER_CONTRACT.yaml`
- English `CACHE_COHERENCE_MODEL.yaml`
- English `MEMORY_VISIBILITY_REPORT.yaml`
- English `DRAM_SCHEDULING_REPORT.yaml`
- English `WARP_MEMORY_TRANSACTION_SPEC.md`
- English `COALESCER_SPEC.md`
- English `SHARED_MEMORY_BANK_CONFLICT_SPEC.md`
- English `L1_CACHE_STATUS_SPEC.md`
- English `MSHR_RESERVATION_FAIL_SPEC.md`
- English `MEMORY_RETURN_PATH_SPEC.md`

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
- warp memory transaction contract
- coalescer contract
- shared memory bank conflict contract
- L1 cache status contract
- MSHR and reservation failure contract
- memory return and scoreboard release contract

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

## Warp Memory Transaction Contract

Memory-capable designs must define lane access -> `warp_memory_transaction`
before cache, L2, DRAM, or return-path attribution. Required fields are warp id,
PC, instruction id, access type, lane addresses, active mask, byte mask, sector
mask, transaction address, transaction size, coalesced group id, and read/write
or atomic flags.

## Coalescer Contract

Coalescer input is per-lane address, active mask, access size/type, byte enables,
and policy. Output is an ordered list of transactions with split reason and
amplification counters. NVIDIA-generation coalescing rules require an optional
compatibility profile.

## Shared Memory Bank Conflict Contract

Shared memory bank conflict is separate from global memory coalescing. It must
record bank mapping, lane-to-bank map, conflict count/class, broadcast policy,
stall reason `shared_bank_conflict`, and release event.

## L1 Cache Status Contract

Cache status must distinguish `HIT`, `HIT_RESERVED`, `MISS`, `SECTOR_MISS`,
`MSHR_HIT`, and `RESERVATION_FAIL`. Reservation fail must further identify
`LINE_ALLOC_FAIL`, `MISS_QUEUE_FULL`, `MSHR_ENTRY_FAIL`,
`MSHR_MERGE_ENTRY_FAIL`, or `MSHR_RW_PENDING`.

## MSHR / Reservation Failure Contract

MSHR evidence must include request id, cache level, MSHR id, allocation attempt,
merge attempt, fail reason, queue occupancy, and replay or release event. Do not
classify structural resource pressure as locality miss.

## Memory Return / Scoreboard Release Contract

Return-path contracts must preserve request id, original warp id, destination
register, response packet id, return queue boundary, final response event, and
scoreboard release event. Loads and atomics must not release scoreboard before
the final core-visible response.

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
- `shared/tables/stall_reason_taxonomy.md`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/warp_memory_transaction.schema.yaml`
- `shared/schemas/coalescer_output_trace.schema.yaml`
- `shared/schemas/cache_request_status.schema.yaml`
- `shared/schemas/memory_request_lifecycle.schema.yaml`
- `shared/schemas/memory_queue_boundary.schema.yaml`

## Required Invariants

The output must satisfy:
- DRAM_CONTROLLER_CONTRACT defines ordering, burst scheduling, and bank-level parallelism model
- CACHE_COHERENCE_MODEL defines writeback vs write-through policy and cross-SM coherence
- cache coherence never changes atomic visibility rules without atomic-sync ownership
- every memory visibility claim cites source SM, address range, request order, and response order
- memory path order is lane access, warp transaction, coalesced request, shared/L1 decision, cache status, MSHR decision, lower memory packet, return, scoreboard release
- every memory instruction must produce a `warp_memory_transaction` or explicit disabled-feature/trap reason
- shared bank conflict, global coalescing, L1 miss, L1 reservation fail, MSHR merge, MSHR allocation fail, ICNT injection fail, return path stall, and scoreboard release wait must be distinct
- cache miss and reservation fail must not be merged
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
- `warp_memory_transaction_contract.md`
- `coalescer_contract.md`
- `shared_memory_bank_conflict_contract.md`
- `l1_cache_status_contract.md`
- `mshr_reservation_fail_contract.md`
- `memory_return_scoreboard_release_contract.md`
- `shared/schemas/warp_memory_transaction.schema.yaml`
- `shared/schemas/cache_request_status.schema.yaml`
- `shared/schemas/memory_request_lifecycle.schema.yaml`
- `shared/templates/warp_memory_transaction_contract.md`
- `shared/templates/memory_queue_boundary_report.md`

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
