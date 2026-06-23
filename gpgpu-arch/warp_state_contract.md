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
owned by `gpgpu-golden` and `gpgpu-rtl`.

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
