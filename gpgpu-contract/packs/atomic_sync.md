# Atomic and Synchronization Contract Pack

Preserved concepts: atomic serialization point, `serialization_point`, `serialization_sequence`, `visibility_event`, `response_to_warp`, `barrier_phase`, `arrival_bitmap`, `release_bitmap`, `lsu_drain_required`, `fence_visibility`, `drain_begin_event`, `drain_end_event`, `completion_condition`, WSYNC prior-work drain, `prior_work_count`, `pending_memory_ops`, and memory ordering litmus tests.

## When to Load

Load when `CAPABILITY_PROFILE_IR.enabled_packs` includes `atomic_sync`, or when the design requires atomics, fence, barrier, CTA synchronization, WSYNC drain, or memory consistency.

## Owned Contract Fragments

Own only the contract fragments named by this pack. The frozen truth remains `SYSTEM_CONTRACT_IR`; pack details must become explicit contract paths before RTL or toolchain use.

## Atomic Operation Contract

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Atomic Execution Model

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Atomic Serialization Point

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## CTA Barrier Contract

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Barrier Phase Contract

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Fence Scope and Visibility

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Wsync Drain Contract

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Memory Ordering Litmus Tests

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Synchronization Stall Attribution

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Golden Semantics Hooks

Expose hook names and state transitions for deriving `GOLDEN_CONTRACT_MODEL` only from `SYSTEM_CONTRACT_IR`.

## RTL Binding Hooks

Expose contract paths, negotiated interface edges, trace events, and counter tap points that RTL may bind without inventing semantics.

## Validation Gates

Require compact pass evidence, first-divergence capture when mismatched, and regression fingerprints for the touched contract paths.

## Failure Modes

Reject missing provenance, simulator-only behavior, unowned semantics, unobservable state transitions, and outputs that bypass `RUN_STATE.yaml`.

## Merged Source Material

### Source ID: `gpgpu-contract/packs/atomic_sync/SKILL.md`

---
name: gpgpu-contract/packs/atomic_sync
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
- `gpgpu-architecture`
- `gpgpu-contract/packs/interconnect`
- `gpgpu-contract/packs/memory_path`
- `gpgpu-rtl`

Downstream:
- `gpgpu-contract`
- `gpgpu-validation`
- `gpgpu-loop`

## Input IR

Consumes:
- `ARCH_IR`
- `CAPABILITY_PROFILE_IR`
- `SM_TO_MEMORY_FABRIC_IR`
- `CACHE_COHERENCE_MODEL`
- memory and atomic traces
- barrier and fence traces
- `shared/references/source_summaries/vortex.md`

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
- `XIANGSHAN_BASIC_AND_FULL_DIFF`
- `XIANGSHAN_STRUCTURED_TRACE_DB`

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
- `shared/tables/workflow_policy.yaml`
- `shared/tables/rewrite_rules.yaml`
- `shared/tables/performance_taxonomy.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/contract_fragment_ir.schema.yaml` (`SYNC_SIDECHANNEL_EVENT`)

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

## Compact Coverage Required

This compact pack is incomplete unless these merged source IDs are present below:
- `atomic_execution_model`
- `barrier_fence_contract`
- `atomic_operation_contract`
- `fence_scope_visibility_contract`
- `cta_barrier_contract`
- `memory_ordering_litmus_tests`
- `synchronization_stall_attribution`

It must also use `shared/schemas/contract_fragment_ir.schema.yaml`.

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.

### Source ID: `gpgpu-contract/packs/atomic_sync/atomic_execution_model.md`

# Atomic Execution Model

This contract defines atomic ordering and visibility.

## Atomic Serialization Point

atomic serialization point must be exactly one of:
- L2 slice
- memory controller
- dedicated atomic unit
- explicitly unsupported trap path

The selected point must be recorded per memory scope.

## Per-SM Atomic Ordering

per-SM atomic ordering must define:
- source SM order
- warp order
- issue order
- serialization order
- response order
- visibility completion event

The model must state whether atomics from the same SM can pass non-atomic memory
operations and which fences prevent that.

## Global Atomic Consistency Model

global atomic consistency model must define:
- total order per address or per scope
- conflict granularity
- read-modify-write visibility
- interaction with cache coherence
- interaction with DRAM scheduling
- trace event that proves serialization

## Required Trace Fields

Atomic trace events must include:
- `sm_id`
- `warp_id`
- `pc`
- `address`
- `operation`
- `old_value`
- `new_value`
- `serialization_point`
- `serialization_sequence`
- `visibility_event`

## Acceptance

`full_memory_sync_system` atomic support passes only if:
- atomic ordering defined
- serialization point is explicit
- per-SM and global ordering are distinguishable
- cache/coherence visibility agrees with the atomic model

### Source ID: `gpgpu-contract/packs/atomic_sync/atomic_operation_contract.md`

# Atomic Operation Contract

Required fields:

- operation type;
- address;
- lane mask;
- byte mask;
- return-value behavior;
- destination register if any;
- completion event;
- serialization domain;
- scoreboard release condition.

Atomic stalls use `atomic_wait` or `atomic_split_or_replay`, not generic memory
stall.

### Source ID: `gpgpu-contract/packs/atomic_sync/atomic_serialization_contract.md`

# Atomic Serialization Contract

Atomic behavior is separate from ordinary load/store coalescing and separate
from fence visibility.

```yaml
atomic_execution:
  operation:
  address:
  serialization_point:
  serialization_sequence:
  old_value:
  new_value:
  visibility_event:
  response_to_warp:
```

Rules:

- Atomic traffic must not be coalesced with ordinary load/store traffic unless
  this contract explicitly permits it.
- Atomic operation must name a serialization point.
- Atomic response must return to the original warp and lane.
- Atomic visibility and fence visibility are different events.

### Source ID: `gpgpu-contract/packs/atomic_sync/barrier_fence_contract.md`

# Barrier and Fence Contract

This contract defines hierarchical barrier and fence semantics.

## Barrier Scopes

Supported barrier scopes:
- warp barrier
- SM barrier
- grid barrier

The canonical execution unit is the warp; SM and grid barriers are broader
contracts with explicit participant sets.

## Warp Barrier

A warp barrier synchronizes active lanes inside one warp. It must
define:
- participating lane mask
- release condition
- interaction with EXEC mask
- trace event

## SM Barrier

A SM barrier synchronizes warps resident in one SM or one workgroup mapped
to one SM. It must define:
- participant warp set
- arrival bitmap
- release bitmap
- timeout or unsupported condition
- LDS visibility rule

## Grid Barrier

A grid barrier synchronizes across SMs. It must define:
- participant SM set
- global arrival count
- memory visibility rule
- unsupported fallback if the hardware/runtime cannot guarantee it

## Fence Ordering Semantics

fence ordering semantics must define:
- scope: warp, SM, device, or system
- affected memory spaces
- request drain condition
- cache visibility action
- atomic interaction
- completion event

## WSYNC / Warp-Sync Drain

`WSYNC` or a warp-sync drain is not a regular scoreboard hazard:

- it does not modify EXEC mask
- it waits for work issued before the sync instruction to retire
- it releases on pending-work drain, not on ordinary register wakeup
- it must emit a trace event with `sm_id`, `warp_id`, prior-work count, and release cycle

## BAR / Barrier Semantics

`BAR` must define:

- arrival event
- participant set
- phase
- wait mask
- release mask
- local memory / LSU drain condition
- optional async arrive/wait fields

Unsupported async barrier modes must be rejected rather than accepted silently.

## Hierarchical Rule

hierarchical barrier and fence semantics:
- warp barrier must not imply SM barrier
- SM barrier must not imply grid barrier unless explicitly declared
- fence scope must be at least as large as the memory visibility claim
- grid barrier requires fabric and memory-system participation

## Failure Modes

Failures include:
- barrier participant mismatch
- fence drain incomplete
- missing memory visibility action
- grid barrier used when unsupported
- barrier/fence trace missing scope
- `WSYNC_CLASSIFIED_AS_SCOREBOARD_HAZARD`
- `BARRIER_RELEASE_WITHOUT_LSU_DRAIN`
- `BARRIER_PHASE_ADVANCE_MISMATCH`
- `ASYNC_BARRIER_UNSUPPORTED_BUT_ACCEPTED`

## XiangShan Sync Side-Channel Events

Barrier, fence, atomic, and WSYNC behavior must emit `SYNC_SIDECHANNEL_EVENT`
records for full transaction diff. These events are side-channel evidence for
synchronization ownership; they do not replace architectural state diff.
Required structured tables include `BARRIER_EVENT_LOG`, `FENCE_EVENT_LOG`, and
`ATOMIC_EVENT_LOG` when those features are enabled.

### Source ID: `gpgpu-contract/packs/atomic_sync/barrier_phase_contract.md`

# Barrier Phase Contract

Barrier is a participant coordination primitive. It is not a fence unless the
contract explicitly adds a memory drain or visibility rule.

```yaml
barrier_phase:
  barrier_id:
  scope: warp | sm | grid
  phase:
  participant_set:
  arrival_bitmap:
  wait_mask:
  release_bitmap:
  lsu_drain_required:
  release_cycle:
```

Rules:

- Barrier release cannot substitute for memory visibility by default.
- If barrier requires LSU drain, the drain must complete before release.
- `BARRIER_PHASE_MISMATCH` routes to `SYNC_ATOMIC_PATCH`.

### Source ID: `gpgpu-contract/packs/atomic_sync/cta_barrier_contract.md`

# CTA Barrier Contract

Barrier fields:

- CTA id;
- expected participant count;
- arrival mask;
- release condition;
- waiting warp list;
- release event.

Barrier wait requires participant and release evidence.

### Source ID: `gpgpu-contract/packs/atomic_sync/fence_scope_visibility_contract.md`

# Fence Scope / Visibility Contract

Fence fields:

- scope;
- ordering domain;
- affected memory spaces;
- visibility point;
- completion condition;
- cache flush or invalidate policy;
- stall reason.

Fence completion must not be defined by a fixed timing delay.

### Source ID: `gpgpu-contract/packs/atomic_sync/fence_visibility_contract.md`

# Fence Visibility Contract

Fence is a memory visibility primitive, not a barrier.

```yaml
fence_visibility:
  fence_scope: warp | sm | device | system
  affected_memory_spaces:
  drain_begin_event:
  drain_end_event:
  pre_fence_write_set:
  post_fence_read_visibility:
  completion_condition:
```

Rules:

- Fence does not require all warps to arrive.
- Fence completion must be later than the required visibility event.
- `FENCE_DRAIN_INCOMPLETE` routes to `SYNC_ATOMIC_PATCH`.

### Source ID: `gpgpu-contract/packs/atomic_sync/memory_ordering_litmus_tests.md`

# Memory Ordering Litmus Tests

Minimum litmus coverage:

- atomic return-value ordering;
- same-address atomic serialization;
- fence visibility point;
- CTA barrier release;
- store/fence/load ordering by scope;
- scoreboard release after atomic or load completion.

GPGPU-Sim timing-side notes are insufficient as a full memory consistency model.

### Source ID: `gpgpu-contract/packs/atomic_sync/synchronization_stall_attribution.md`

# Synchronization Stall Attribution

Stable synchronization stall reasons:

- `atomic_wait`
- `atomic_split_or_replay`
- `membar_wait`
- `fence_flush_or_invalidate`
- `barrier_wait`

Each reason requires a synchronization contract event and a release condition.

### Source ID: `gpgpu-contract/packs/atomic_sync/wsync_drain_contract.md`

# WSYNC Drain Contract

WSYNC is prior-work drain, not a normal scoreboard wakeup.

```yaml
wsync_drain:
  sm_id:
  warp_id:
  prior_work_count:
  pending_memory_ops:
  pending_long_latency_ops:
  drain_begin:
  drain_end:
  release_event:
```

Failure modes:

- `WSYNC_CLASSIFIED_AS_SCOREBOARD_HAZARD`
- `WSYNC_RELEASE_BEFORE_PRIOR_WORK_DRAIN`
- `BARRIER_RELEASE_WITHOUT_LSU_DRAIN`
- `FENCE_COMPLETES_BEFORE_VISIBILITY`
