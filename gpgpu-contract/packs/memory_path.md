# Memory Path Contract Pack

Preserved concepts: `MEMORY_BUNDLE`, `lsu_lane_request`, `per_lane_addr`, `byte_enable`, `lane_mask`, coalescer request merge, response restore, `final_eop`, `nonblocking_memory_tag`, allocated_on accepted_load_or_atomic_request, released_on final_core_visible_response_eop, `local_memory_bank`, `bank_mapping_function`, `l1_cache_or_global_adapter`, `l2_cache_slice`, `mshr_replay_contract`, `dram_controller_contract`, `memory_visibility`, scoreboard release, and shared memory bank conflict.

## When to Load

Load when `CAPABILITY_PROFILE_IR.enabled_packs` includes `memory_path`, or when the design requires shared/global/local memory, coalescer behavior, cache behavior, L1/global adapter, L2 slice, MSHR/replay, DRAM boundary, or memory visibility.

## Owned Contract Fragments

Own only the contract fragments named by this pack. The frozen truth remains `SYSTEM_CONTRACT_IR`; pack details must become explicit contract paths before RTL or toolchain use.

## Warp Memory Transaction

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## LSU Lane Request Format

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Coalescer Request Merge and Response Restore

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Shared/Local Memory Banks

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## L1 Cache or Global Adapter

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## L2 Cache Slice

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## MSHR, Replay, Reservation Fail, and Deadlock Guard

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## DRAM Controller Boundary

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Memory Visibility

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Scoreboard Release

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

### Source: `skill/gpgpu-contract/packs/memory_path/SKILL.md`

---
name: gpgpu-contract/packs/memory_path
description: Use when DRAM controller behavior, L2/cache hierarchy, cache coherence, cross-SM memory visibility, memory ordering, or shared-memory-system contracts must be defined or validated.
---

# GPGPU Memory System Contract Engine

## Role

This skill owns the `full_memory_sync_system` memory-system contract after requests leave the
interconnect fabric. It defines DRAM scheduling, cache write policy, coherence,
visibility, and memory hierarchy evidence.

## Position in Flow

Upstream:
- `gpgpu-architecture`
- `gpgpu-contract/packs/interconnect`
- `gpgpu-rtl`

Downstream:
- `gpgpu-contract`
- `gpgpu-contract/packs/atomic_sync`
- `gpgpu-validation`
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
- `XIANGSHAN_BASIC_AND_FULL_DIFF`
- `XIANGSHAN_STRUCTURED_TRACE_DB`

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
- define atomic serialization point independently from `gpgpu-contract/packs/atomic_sync`
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
- `shared/schemas/memory_transaction_event.schema.yaml` (`MEMORY_TRANSACTION_EVENT`)

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

### Source: `skill/gpgpu-contract/packs/memory_path/cache_coherence_model.md`

# Cache Coherence Model

This contract defines cross-SM cache and memory visibility.

## Cache Policy

writeback vs write-through policy must be explicit for each cache hierarchy tier:
- private L1 cache
- shared L2 cache
- write-combining buffer if present
- uncached path if present

Required fields:
- line size
- write allocate policy
- replacement visibility caveat
- dirty state owner
- invalidation or update mechanism
- response ordering rule

## Atomic Visibility Rules

atomic visibility rules are consumed from `gpgpu-contract/packs/atomic_sync`. This memory skill
records how the cache hierarchy preserves or forwards atomic visibility, but it
does not independently choose the atomic serialization point.

Required fields:
- atomic path
- line lock or bypass rule
- visibility completion event
- cache invalidation or update action

## Cross-SM Coherence

cross-SM coherence must define:
- which writes become visible to other SMs
- when reads can observe another SM's writes
- how L1 private caches interact with shared L2
- whether LDS is excluded from cross-SM visibility
- how fences force visibility

## Coherence State Model

Minimal allowed states:
- `INVALID`
- `SHARED`
- `EXCLUSIVE`
- `MODIFIED`
- `BYPASS`

Simpler designs may use a subset, but must state which states are absent and
why correctness still holds.

## Failure Modes

Failures include:
- stale read across SM
- write visibility missing
- dirty writeback lost
- invalidation missing
- atomic visibility violation
- fence visibility violation

### Source: `skill/gpgpu-contract/packs/memory_path/cache_response_routing_contract.md`

# Cache Response Routing Contract

Cache response routing is responsible for returning fills, hits, replays,
writebacks, atomics, and bypass responses to the original core-visible request.

```yaml
cache_response_routing:
  source_sm_id:
  source_warp_id:
  source_request_tag:
  response_tag:
  l2_slice_id:
  cache_bank_id:
  mshr_id:
  restored_lane_mask:
  final_eop:
```

Failure modes:

- `CACHE_RESPONSE_ROUTING_MISMATCH`
- `RESPONSE_DEMUX_MISMATCH`
- `MEMORY_TAG_REUSE_BEFORE_EOP`

### Source: `skill/gpgpu-contract/packs/memory_path/coalescer_contract.md`

# Coalescer Contract

Input:

- per-lane address;
- active mask;
- access size;
- access type;
- byte enables;
- coalescing policy.

Output:

- ordered transactions;
- coalesced group id;
- transaction mask;
- split reason;
- amplification counter.

Do not copy NVIDIA-generation coalescing rules unless a compatibility profile
selects them.

## Structured Trace Requirements

Coalescer features must provide `COALESCER_LOG` as a
`STRUCTURED_TRACE_TABLE`, plus one `SQL_DEBUG_QUERY` for mismatch localization
and one `SQL_PERF_QUERY` for request-reduction or amplification attribution.

### Source: `skill/gpgpu-contract/packs/memory_path/coalescer_response_restore_contract.md`

# Coalescer Response Restore Contract

coalescer correctness = request merge correctness + response restore correctness

```yaml
coalescer_merge:
  original_requests:
    - original_tag
    - lane_mask
    - per_lane_addr
    - per_lane_offset
    - byte_enable
  coalesced_request:
    coalesced_tag
    line_addr
    merged_byte_enable
    merged_lane_mask

coalescer_restore:
  coalesced_tag:
  original_tag:
  restored_lane_mask:
  restored_lane_data:
  final_eop:
```

Failure modes:

- `COALESCER_MERGE_UNSAFE`
- `COALESCER_RESPONSE_SHAPE_MISMATCH`
- `COALESCER_TAG_REUSE_BEFORE_EOP`
- `COALESCER_BYTE_ENABLE_RESTORE_MISMATCH`

### Source: `skill/gpgpu-contract/packs/memory_path/dram_controller_contract.md`

# DRAM Controller Contract

This contract defines `full_memory_sync_system` DRAM behavior visible to GPGPU correctness and
performance attribution.

## Memory Request Ordering

memory request ordering must define:
- source SM order
- address order
- read/write order
- fence drain order
- atomic order handoff
- response return order

The contract must distinguish required architectural order from performance
reordering that preserves visibility.

## Burst Scheduling

burst scheduling must define:
- burst size
- row-hit policy
- read/write turnaround policy
- queue selection policy
- starvation bound or explicit caveat
- trace fields for selected bank and row

## Bank-Level Parallelism Model

bank-level parallelism model must define:
- bank count
- bank address mapping
- row buffer state if modeled
- bank conflict detection
- concurrent bank access limits
- bank conflict stall attribution

## Trace Evidence

Required DRAM trace fields:
- request ID
- source SM
- L2 slice
- DRAM channel
- bank
- row
- burst length
- queue wait
- service cycles
- response ID

## Acceptance

`full_memory_sync_system` DRAM passes only if:
- DRAM controller contract defined
- memory request ordering is explicit
- bank-level parallelism model is present
- burst scheduling is auditable
- performance stalls can distinguish DRAM bank conflict from NoC/L2 contention

### Source: `skill/gpgpu-contract/packs/memory_path/l1_cache_or_global_adapter_contract.md`

# L1 Cache or Global Adapter Contract

`L1 cache` is a hardware cache term. A capability profile may choose either a
private L1 cache or a direct global adapter.

```yaml
l1_cache_or_global_adapter:
  mode: direct_global_adapter | private_l1_cache
  hit_policy:
  miss_policy:
  mshr_required:
  write_policy:
  response_order_policy:
  visibility_boundary:
```

If `mode: direct_global_adapter`, the contract must still say whether hit/miss,
MSHR, response reorder, and visibility effects exist. Hidden default behavior is
not allowed.

### Source: `skill/gpgpu-contract/packs/memory_path/l1_cache_status_contract.md`

# L1 Cache Status Contract

Cache status values:

- `HIT`
- `HIT_RESERVED`
- `MISS`
- `SECTOR_MISS`
- `MSHR_HIT`
- `RESERVATION_FAIL`

Reservation fail reasons:

- `LINE_ALLOC_FAIL`
- `MISS_QUEUE_FULL`
- `MSHR_ENTRY_FAIL`
- `MSHR_MERGE_ENTRY_FAIL`
- `MSHR_RW_PENDING`

Never merge cache misses with reservation failures.

### Source: `skill/gpgpu-contract/packs/memory_path/l1_coalescer_cache_contract.md`

# L1 Coalescer Cache Contract

This contract defines the L1-side obligations for coalesced memory traffic.

Required fields:

- line size
- bank mapping
- MSHR tag expansion
- request queue almost-full gating
- response queue backpressure
- replay ordering
- read/write replay policy

The L1 path must prove whether a request was merged, split, replayed, or
blocked by almost-full state. A cache performance claim is not valid unless the
trace can connect original lane request shape to cache-bank request shape and
then back to restored lane response shape.

Failure modes:

- `COALESCER_RESPONSE_SHAPE_MISMATCH`
- `COALESCER_TAG_RESTORE_MISMATCH`
- `CACHE_REPLAY_ORDER_MISMATCH`
- `WRITE_REPLAY_POLICY_UNDEFINED`
- `READ_REPLAY_POLICY_UNDEFINED`

### Source: `skill/gpgpu-contract/packs/memory_path/l2_cache_slice_contract.md`

# L2 Cache Slice Contract

`L2 cache slice` is a hardware cache component used by
`full_memory_sync_system`.

```yaml
l2_cache_slice:
  l2_slice_id:
  bank_id:
  line_addr:
  cache_tag:
  mshr_id:
  request_queue_occupancy:
  response_queue_occupancy:
  replay_policy:
  fill_policy:
  writeback_policy:
  response_demux_target:
```

The slice must preserve source SM, source warp, request tag, lane mask, and byte
enable through miss, fill, replay, and response demux.

### Source: `skill/gpgpu-contract/packs/memory_path/local_memory_bank_contract.md`

# Local Memory Bank Contract

Shared memory and local memory are SM-local unless the frozen system contract
states otherwise.

```yaml
local_memory_bank:
  sm_id:
  bank_count:
  bank_mapping_function:
  conflict_policy:
  read_during_write_policy:
  response_hold_register:
  backpressure_behavior:
  barrier_visibility_rule:
```

Required tests:

- shared memory bank conflict;
- same-bank multi-lane access;
- response held under downstream backpressure;
- barrier after shared memory access waits for required visibility.

### Source: `skill/gpgpu-contract/packs/memory_path/lsu_lane_format_contract.md`

# LSU Lane Format Contract

This contract is derived from the Vortex `VX_lsu_slice` lesson. The LSU
front-end must preserve lane shape before any cache, coalescer, or fabric step.

```yaml
lsu_lane_request:
  sm_id:
  warp_id:
  instruction_uuid:
  lane_mask:
  per_lane_addr:
  aligned_addr:
  access_size:
  byte_enable:
  store_data_shifted:
  memory_space: shared | global | constant | local
  load_format_rule: raw | sign_extend | zero_extend | nan_box
```

Acceptance requires traceable address alignment, byte enable, shifted store
data, load response formatting, and lane mask preservation.

### Source: `skill/gpgpu-contract/packs/memory_path/memory_response_routing.md`

# Memory Response Routing

Every memory response must preserve the identity needed to wake exactly the
original requester.

Required route:

- cache bank tag -> wrapper tag -> original request tag
- SM / warp / lane identity preservation
- final response release to scoreboard
- fault response routing to completion/fault observation

Required response fields:

- `response_tag`
- `original_request_tag`
- `sm_id`
- `warp_id`
- `lane_mask`
- `byte_enable`
- `per_lane_offset`
- `restored_lane_data`
- `final_eop`
- `scoreboard_release_event`

Failure modes:

- `RESPONSE_ROUTING_MISMATCH`
- `TAG_REUSE_BEFORE_RESPONSE`
- `SCOREBOARD_WAKEUP_BEFORE_FINAL_RESPONSE`
- `COALESCER_RESPONSE_SHAPE_MISMATCH`

## XiangShan Memory Transaction Event

Full transaction diff must emit `MEMORY_TRANSACTION_EVENT` for accepted load,
store, atomic, coalesced request, cache refill, MSHR replay, response restore,
and final scoreboard release. Each event must preserve request tag, response
tag, original request tag, SM, warp, lane mask, byte enable, and final EOP.

### Source: `skill/gpgpu-contract/packs/memory_path/memory_return_scoreboard_release_contract.md`

# Memory Return / Scoreboard Release Contract

Return path must preserve:

- request id;
- original warp id;
- destination register;
- response packet id;
- return queue boundary;
- final response event;
- scoreboard release event.

Loads and atomics with destination registers must not release scoreboard before
the final core-visible response.

### Source: `skill/gpgpu-contract/packs/memory_path/memory_visibility_contract.md`

# Memory Visibility Contract

Memory visibility is a correctness contract, not a cache implementation detail.

```yaml
memory_visibility:
  visibility_event:
  visibility_scope: warp | sm | device | system
  affected_memory_spaces:
  producer_event:
  consumer_event:
  ordering_scope:
  required_drain_events:
```

Rules:

- Fence visibility is owned jointly with `gpgpu-contract/packs/atomic_sync`.
- Barrier release does not imply memory visibility unless the contract says so.
- Atomic visibility and fence visibility are separate events.

### Source: `skill/gpgpu-contract/packs/memory_path/mshr_deadlock_guard.md`

# MSHR Deadlock Guard

Cache and coalescer pipelines must declare structural guards before accepting a
request that can allocate downstream resources.

Required guards:

- `mshr_alm_full`
- `request_queue_alm_full`
- `response_queue_alm_full`
- no request accepted unless the response path can eventually drain

The guard must be part of the contract, trace, and unit-test evidence. A design
that only detects deadlock after timeout must emit `MSHR_DEADLOCK_GUARD_MISSING`.

Acceptance evidence:

- directed test with nearly full MSHR
- directed test with nearly full request queue
- directed test with response backpressure
- trace showing accepted request count never exceeds guaranteed drain capacity

### Source: `skill/gpgpu-contract/packs/memory_path/mshr_replay_contract.md`

# MSHR Replay Contract

```yaml
mshr_replay_contract:
  allocate_on: cache_miss
  hold_context:
    - source_sm_id
    - source_warp_id
    - source_request_tag
    - line_addr
    - byte_enable
    - lane_mask
  replay_order_policy:
  fill_completion_event:
  release_event:

mshr_deadlock_guard:
  block_new_request_if:
    - mshr_almost_full
    - memory_request_queue_almost_full
    - response_queue_almost_full
    - writeback_egress_blocked
    - replay_queue_blocked
```

`MSHR_REPLAY_MISMATCH` routes to `MEMORY_PATH_PATCH`.

### Source: `skill/gpgpu-contract/packs/memory_path/mshr_reservation_fail_contract.md`

# MSHR / Reservation Failure Contract

MSHR evidence must include:

- request id;
- cache level;
- MSHR id;
- allocation attempt;
- merge attempt;
- fail reason;
- queue occupancy;
- replay or release event.

Reservation failures are structural resource pressure, not locality misses.

### Source: `skill/gpgpu-contract/packs/memory_path/nonblocking_memory_tag_contract.md`

# Nonblocking Memory Tag Contract

Nonblocking memory tags are allocated resources. They are not released by raw
fabric responses; they release only after the final core-visible response EOP.

```yaml
nonblocking_memory_tag:
  allocated_on: accepted_load_or_atomic_request
  released_on: final_core_visible_response_eop
  tag_payload:
    - sm_id
    - warp_id
    - instruction_uuid
    - original_lane_mask
    - byte_enable_vector
    - scoreboard_destination
    - response_restore_context
```

Forbidden behavior:

- raw memory response releases scoreboard;
- response without `final_eop` releases tag;
- tag reuse before final core-visible response.

### Source: `skill/gpgpu-contract/packs/memory_path/shared_memory_bank_conflict_contract.md`

# Shared Memory Bank Conflict Contract

Shared memory conflicts are not global memory coalescing.

Required evidence:

- bank mapping function;
- lane-to-bank map;
- conflict count or class;
- broadcast policy;
- stall reason `shared_bank_conflict`;
- release event.

Do not use fixed shared-memory latency as the contract.

### Source: `skill/gpgpu-contract/packs/memory_path/warp_memory_transaction_contract.md`

# Warp Memory Transaction Contract

Required fields:

- warp id;
- PC;
- instruction id;
- access type;
- lane addresses;
- active mask;
- byte mask;
- sector mask;
- transaction address;
- transaction size;
- coalesced group id;
- read/write/atomic flags.

This is the first memory boundary.
