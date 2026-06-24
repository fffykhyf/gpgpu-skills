# Capability Profiles

## Merged Source Material

### Source ID: `gpgpu-architecture/capability_profile_and_preset.md`

# Capability Profile and Preset Contract

`gpgpu-architecture` selects a `capability_profile` before emitting `ARCH_IR`.
Profiles name GPU capability domains, not development stages. Numeric stage
names are not valid profile names because they conflict with hardware cache
terms such as L1 cache and L2 cache.

## Capability Profile

```yaml
capability_profile:
  name: minimal_simt_core |
        single_sm_warp_pipeline |
        toolchain_runtime_vertical_slice |
        multi_sm_memory_path |
        full_memory_sync_system

  enabled_subsystems:
    - simt_core
    - warp_scheduler
    - scoreboard
    - divergence_unit
    - lsu
    - shared_memory
    - coalescer
    - l1_cache_or_global_adapter
    - interconnect_fabric
    - l2_cache_slice
    - dram_controller
    - atomic_unit
    - fence_unit
    - barrier_unit
```

## Presets

```yaml
MINIMAL_SIMT_CORE:
  capability_profile: minimal_simt_core
  sm_count: 1
  warp_count: 1
  memory_path: simple_global_memory
  runtime_required: false

SINGLE_SM_WARP_PIPELINE:
  capability_profile: single_sm_warp_pipeline
  sm_count: 1
  warp_count: multiple
  scoreboard: required
  divergence: required
  lsu: required

TOOLCHAIN_RUNTIME_VERTICAL_SLICE:
  capability_profile: toolchain_runtime_vertical_slice
  assembler: required
  disassembler: required
  program_image: required
  loader: required
  runtime_launch: required
  rtl_smoke: required
  golden_dump: required

MULTI_SM_MEMORY_PATH:
  capability_profile: multi_sm_memory_path
  sm_count: multiple
  shared_memory: required
  coalescer: required
  l1_cache_or_global_adapter: required
  response_restore: required
  sm_id_routing: required

FULL_MEMORY_SYNC_SYSTEM:
  capability_profile: full_memory_sync_system
  fabric: required
  l2_cache_slice: required
  mshr: required
  dram_controller: required
  atomic_unit: required
  fence_unit: required
  barrier_unit: required
  memory_visibility_model: required
```

## Ownership Rules

- `gpgpu-architecture` chooses the profile and emits candidate architecture nodes.
- `gpgpu-contract/packs/interconnect`, `gpgpu-contract/packs/memory_path`, and `gpgpu-contract/packs/atomic_sync` emit
  `contract_fragment_ir` for enabled subsystems before golden freeze.
- `gpgpu-contract` freezes fragments into `SYSTEM_CONTRACT_IR`.
- Cache terms remain hardware terms only: write `L1 cache`, `L2 cache`, or
  `L2 cache slice` only when describing real cache hierarchy.

## Required Acceptance

A generated `ARCH_IR` is accepted only if:

- it contains `capability_profile`;
- enabled subsystems match the selected profile;
- graph nodes name the owner skill for every fragment-producing subsystem;
- unsupported subsystems are explicit non-goals;
- the selected preset is recorded with provenance and rejected alternatives.

## XiangShan Runtime DSE Boundary

`XIANGSHAN_SAFE_RUNTIME_DSE` adds a required parameter classification before
DSE. Every parameter must produce `KNOB_CLASSIFICATION`:

- `structural_compile_time`: module count, wire width, queue depth, bank count,
  data width, warp size, register-file geometry
- `abi_visible`: ISA encoding, launch descriptor layout, MMIO register map,
  memory consistency scope
- `runtime_behavior_knob`: scheduler policy select, coalescer policy select,
  prefetch enable, replay threshold, throttle threshold
- `debug_trace_knob`: memory trace, scoreboard trace, barrier trace, full
  transaction diff, counter selection

Only runtime behavior and debug trace knobs may become `RUNTIME_DSE_KNOB`.

### Source ID: `gpgpu-architecture/scheduler_visible_state_contract.md`

# Scheduler-Visible State Contract

Required scheduler-visible state:

- `warp_state`: valid, exited, CTA id, next PC, ibuffer valid, outstanding
  memory and sync waits.
- `SIMT_state`: warp id, PC, active mask, reconvergence PC, call depth,
  divergence event.
- `Scoreboard_state`: warp id, pending destination registers, long-op
  destination registers, reserve event, release event, collision result.
- `pipe_state`: pipe class, availability, selected issue slot, dual-issue
  restriction.

SIMT owns PC/control masks. Scoreboard owns register dependency hazards.

### Source ID: `gpgpu-architecture/sm_issue_gate_contract_gpgpusim.md`

# SM Issue / Non-Issue Contract

Every generated SM design must expose:

- warp valid and exited state;
- barrier, membar, atomic, and memory-backpressure wait state;
- ibuffer valid bit and instruction PC;
- SIMT top PC and active mask;
- scoreboard collision result;
- target pipe availability;
- dual-issue allow/deny result;
- issue event and scoreboard reserve event.

The canonical issue gate order is:

1. warp valid;
2. not waiting at barrier, membar, atomic, or dependency barrier;
3. ibuffer has instruction;
4. SIMT top PC matches instruction PC;
5. scoreboard has no collision;
6. target pipe has a free slot;
7. dual-issue policy allows;
8. issue and reserve scoreboard.

### Source ID: `gpgpu-architecture/sm_hierarchy_model.md`

# SM Hierarchy Model

This file defines the architecture hierarchy for the SM-centric capability
profiles.
`SM` is the canonical execution island in GPGPU skills.

## Hierarchy

```text
GPU
  -> SM array
      -> SM
          -> Warp pool
          -> Exec context table
          -> SIMD lanes
          -> SGPR bank
          -> VGPR bank
          -> LDS
          -> LSU
          -> Issue Arbiter
          -> Trace adapter
```

## SM is the canonical execution island

A SM is the smallest independently scheduled execution island. It owns the
resident warp resources and the local issue contract.

Required SM fields:
- `sm_id`
- `warp_slots`
- `warp_size_options`
- `issue_width`
- `simd_lane_count`
- `lds_capacity_bytes`
- `sgpr_bank_count`
- `vgpr_bank_count`
- `lsu_frontend_count`
- `memory_port_count`
- `trace_partition_id`

## Required Subsystems

### Warp pool

The warp pool stores resident warp identity, queued fetch/decode packets,
and per-warp resource bases.

Required state:
- resident warp bitmap
- dispatch tag map
- per-warp PC
- SGPR/VGPR/LDS base fields
- instruction queue occupancy
- queue reset causes

### Exec context table

The exec context table owns per-warp control and predicate state.

Required state:
- EXEC mask
- VCC
- SCC
- M0 or target-specific special state
- pending branch bit
- barrier/wait state
- reconvergence stack pointer when enabled

### SIMD lanes

SIMD lanes execute vector operations under EXEC-mask driven gating. The
architecture contract must define whether the design supports 32-thread,
64-thread, or configurable warp widths.

### LDS

LDS is local to the SM unless the system contract explicitly defines a
different scope. LDS addresses must not be treated as a global-memory alias.

### LSU

The LSU front-end consumes decode-time memory bundles, computes per-lane
addresses, forms coalesced transactions, tags the memory space as global or
LDS, and reports completion back to issue state.

### Issue Arbiter

The Issue Arbiter selects ready warp work using an inspectable equation:
decoded valid, FU class, GPR readiness, special-state readiness, memory wait,
branch wait, barrier wait, max in-flight, and FU availability.

## Independence Rule

SM is fully independent execution island.

Required invariant:
- no shared execution state across SM
- no cross-SM dependency for warp residency, PC, EXEC, SGPR, VGPR, LDS, or issue readiness
- cross-SM interaction occurs only through defined memory, atomic, barrier, or system fabric contracts

## Multi-SM Routing

Multi-SM architecture must define:
- `sm_count`
- workgroup-to-SM dispatch mapping
- warp-to-SM residency rule
- SM_ID routing rule for traces and memory requests
- memory fabric request source ID
- per-SM performance counter partition

## Forbidden Architecture Defaults

The generator must not silently emit:
- `sm_count`
- `max_warps_per_sm`
- `warp_scheduler`
- `SM scheduler`
- generic `execution pipeline` as the top execution contract

Use:
- `sm_count`
- `warp_slots_per_sm`
- `warp_scheduler`
- `SM issue model`
- typed decode/issue/memory bundle contracts

## Capability Acceptance

A generated `ARCH_IR` reaches `single_sm_warp_pipeline` or
`multi_sm_memory_path` only if:
- it declares SM as the top execution island
- warp state includes explicit EXEC lifecycle
- LDS is local to SM and separately tagged from global memory
- coalescer policy is contract-defined
- multi-SM independence is enforced

### Source ID: `gpgpu-architecture/warp_state_contract.md`

# Warp State Contract

This contract defines the architecture-layer SM/warp execution contract model.
It is derived from local MIAOW reader reports and Vortex reader reports under
`ref/skillref`, especially the warp lifecycle, EXEC state, fetch snapshot, and
decode/issue reports. Reference mechanisms are evidence for contracts, not
constants to copy.

## Canonical Entity

The architecture generator must model a warp as the resident execution
context inside a SM. A warp owns architectural identity and state, while
the SM owns physical execution resources.

Required identity fields:
- `sm_id`
- `warp_id`
- `dispatch_tag`
- `workgroup_id`
- `cta_or_workgroup_slot_id`
- `cta_rank_or_warp_rank`
- `cta_size_or_workgroup_size`
- `pc`
- `entry_pc`
- `sgpr_base`
- `vgpr_base`
- `lds_base`
- `arg_pointer_or_mscratch`
- `thread_idx_base[3]`
- `block_idx[3]`
- `block_dim[3]`
- `grid_dim[3]`
- `trap_or_fault_csrs`
- `warp_size`
- `exec_mask`
- `active`
- `stalled`
- `retired`

## State Machine

Every warp state machine must define these states:

| State | Meaning |
|---|---|
| `FREE` | No resident work; slot may be allocated by dispatcher. |
| `DISPATCHED` | Workgroup/CTA state has been assigned but fetch has not yet become active. |
| `ACTIVE` | Resident and eligible to fetch, decode, or issue when dependencies permit. |
| `PENDING` | Allocated but waiting for fetch, decode, resource, or dependency readiness. |
| `FETCH_SNAPSHOT` | Scheduled PC, EXEC mask, identity, and launch context have been captured for fetch. |
| `DECODED` | Fetched instruction has decoded into an issue-visible record. |
| `ISSUE_READY` | Decoded record is ready to arbitrate if dependencies and resources permit. |
| `STALLED` | Blocked by scoreboard, issue arbiter, barrier, or structural hazard. |
| `WAITING_MEMORY` | LSU or memory fabric accepted a request and completion has not released the warp. |
| `WAITING_BARRIER` | Barrier state owns release; scheduler may only observe parked/released status. |
| `DIVERGED` | EXEC mask or control path split prevents single-path issue. |
| `RECONVERGING` | Reconvergence stack is draining paths or restoring a saved EXEC mask. |
| `RETIRED` | All architectural effects are complete and the dispatch tag may be returned. |

Allowed state transitions:
- `FREE -> DISPATCHED` when dispatcher assigns a resident slot and launch-visible context.
- `DISPATCHED -> ACTIVE` when the initial PC, EXEC mask, and resource bases are valid.
- `PENDING -> ACTIVE` when fetch slot, warp-pool entry, initial PC, and initial EXEC are valid.
- `ACTIVE -> FETCH_SNAPSHOT` when the scheduler selects the warp for fetch.
- `FETCH_SNAPSHOT -> DECODED` when fetch returns the captured instruction record.
- `DECODED -> ISSUE_READY` when decode produces a valid instruction bundle.
- `ISSUE_READY -> STALLED` when scoreboard, barrier, structural, or issue readiness fails.
- `ACTIVE -> STALLED` when any readiness term is false.
- `STALLED -> ACTIVE` when the owner release event clears the blocking term.
- `ACTIVE -> WAITING_MEMORY` when an LSU memory bundle is issued.
- `WAITING_MEMORY -> ACTIVE` when memory response, writeback, and scoreboard release complete.
- `ACTIVE -> WAITING_BARRIER` when a barrier or wait instruction parks the warp.
- `WAITING_BARRIER -> ACTIVE` when barrier release and required LSU drain are complete.
- `ACTIVE -> DIVERGED` when a branch or mask instruction splits active lanes.
- `DIVERGED -> RECONVERGING` when all lanes for the current path drain.
- `RECONVERGING -> ACTIVE` when the next path restores PC and EXEC.
- `ACTIVE -> RETIRED` only after no decoded entry, no in-flight operation, no memory wait, and no pending branch/barrier remain.

## Fetch Snapshot Rule

Fetch must consume a scheduled snapshot, not live warp state. The snapshot
records `sm_id`, `warp_id`, `cta_or_workgroup_slot_id`, `pc`, `exec_mask`,
`instruction_id_or_uuid`, `sop`, `eop`, and launch-visible context at schedule
time. If icache, decompression, or decode latency returns after live PC/mask
changes, the returned instruction must still use the captured snapshot fields.

Missing snapshot evidence is `TRACE_TAP_INSUFFICIENT_FOR_FIRST_DIVERGENCE`.

## EXEC mask evolution rules

The EXEC mask is architectural per-warp state. It must not be inferred from
warp validity or lane count.

Rules:
- Launch initializes `exec_mask` from explicit warp size or launch lane mask.
- Scalar/control instructions may write EXEC through a single special-state owner.
- Vector compare instructions may write VCC and later influence EXEC through scalar/control instructions.
- SIMD issue gates each lane with the current `exec_mask`.
- Memory bundle lane masks are derived from `exec_mask` plus instruction predicate masks.
- Scoreboard and trace must expose EXEC read/write events and dependency release.
- A zero EXEC mask is legal only if the control contract defines how the warp reaches reconvergence or retirement.

## Branch divergence model

The branch divergence model must be explicit even for minimal designs.

Required fields:
- branch condition source: `SCC`, `VCCZ`, `EXECZ`, predicate, or contract-specific flag
- branch target PC
- fallthrough PC
- pre-branch EXEC mask
- taken-lane mask
- not-taken-lane mask
- selected path order
- reconvergence PC

The generator may choose a simple single-path branch-pending model for
`minimal_simt_core` or `single_sm_warp_pipeline` bring-up, but
`multi_sm_memory_path` and `full_memory_sync_system` contracts must describe
whether a full reconvergence stack is present. If there is no stack, the
missing capability must be explicit.

## Reconvergence stack

The reconvergence stack records divergent paths that must be resumed.

Required stack entry fields:
- `warp_id`
- `resume_pc`
- `resume_exec_mask`
- `reconverge_pc`
- `path_kind`
- `source_branch_pc`

Stack operations:
- `push` on divergence when both taken and not-taken lane masks are non-empty.
- `restore` when the current path drains or reaches reconvergence.
- `pop` when the restored path completes.
- `clear` on warp retirement or fatal fault.

## Contract Boundaries

The architecture layer may decide whether the target design has:
- a branch-pending only model
- a one-level reconvergence stack
- a full nested reconvergence stack

It must not define RTL signal names or golden implementation code. Those are
owned by `gpgpu-contract` and `gpgpu-rtl`.

## Verification Hooks

Required evidence:
- dispatch allocation initializes PC, bases, warp identity, and EXEC mask
- branch changes PC and either updates EXEC or records a divergence stack entry
- special-state write changes EXEC/VCC/SCC in trace-visible form
- retired warp frees its resident slot and dispatch tag

## Do Not Copy From MIAOW

Do not copy MIAOW's 40 resident warp slots, 64-lane mask width, fixed PC
increment, Southern-Islands special-register numbers, or generated RTL style as
defaults. Copy the owner/consumer discipline and lifecycle visibility.
