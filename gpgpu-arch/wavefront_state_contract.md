# Wavefront State Contract

This contract upgrades the architecture layer from an SM-centric warp model to
a CU-centric wavefront execution contract model. It is derived from the local
MIAOW reader reports under `ref/skillref/miaow-reader-reports`, especially the
wavefront lifecycle, EXEC state, and decode/issue reports. MIAOW mechanisms are
used as evidence for contracts, not as constants to copy.

## Canonical Entity

The architecture generator must model a wavefront as the resident execution
context inside a CU. A wavefront owns architectural identity and state, while
the CU owns physical execution resources.

Required identity fields:
- `cu_id`
- `wavefront_id`
- `dispatch_tag`
- `workgroup_id`
- `pc`
- `sgpr_base`
- `vgpr_base`
- `lds_base`
- `wavefront_size`
- `exec_mask`

## State Machine

Every wavefront state machine must define these states:

| State | Meaning |
|---|---|
| `ACTIVE` | Resident and eligible to fetch, decode, or issue when dependencies permit. |
| `PENDING` | Allocated but waiting for fetch, decode, resource, or dependency readiness. |
| `STALLED` | Blocked by scoreboard, issue arbiter, barrier, or structural hazard. |
| `WAITING_MEMORY` | LSU or memory fabric accepted a request and completion has not released the wavefront. |
| `DIVERGED` | EXEC mask or control path split prevents single-path issue. |
| `RECONVERGING` | Reconvergence stack is draining paths or restoring a saved EXEC mask. |
| `RETIRED` | All architectural effects are complete and the dispatch tag may be returned. |

Allowed state transitions:
- `PENDING -> ACTIVE` when fetch slot, wavepool entry, initial PC, and initial EXEC are valid.
- `ACTIVE -> STALLED` when any readiness term is false.
- `STALLED -> ACTIVE` when the owner release event clears the blocking term.
- `ACTIVE -> WAITING_MEMORY` when an LSU memory bundle is issued.
- `WAITING_MEMORY -> ACTIVE` when memory response, writeback, and scoreboard release complete.
- `ACTIVE -> DIVERGED` when a branch or mask instruction splits active lanes.
- `DIVERGED -> RECONVERGING` when all lanes for the current path drain.
- `RECONVERGING -> ACTIVE` when the next path restores PC and EXEC.
- `ACTIVE -> RETIRED` only after no decoded entry, no in-flight operation, no memory wait, and no pending branch/barrier remain.

## EXEC mask evolution rules

The EXEC mask is architectural per-wavefront state. It must not be inferred from
wavefront validity or lane count.

Rules:
- Launch initializes `exec_mask` from explicit wavefront size or launch lane mask.
- Scalar/control instructions may write EXEC through a single special-state owner.
- Vector compare instructions may write VCC and later influence EXEC through scalar/control instructions.
- SIMD issue gates each lane with the current `exec_mask`.
- Memory bundle lane masks are derived from `exec_mask` plus instruction predicate masks.
- Scoreboard and trace must expose EXEC read/write events and dependency release.
- A zero EXEC mask is legal only if the control contract defines how the wavefront reaches reconvergence or retirement.

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

The generator may choose a simple single-path branch-pending model for L2/L3
bring-up, but L3/L4 contracts must describe whether a full reconvergence stack
is present. If there is no stack, the missing capability must be explicit.

## Reconvergence stack

The reconvergence stack records divergent paths that must be resumed.

Required stack entry fields:
- `wavefront_id`
- `resume_pc`
- `resume_exec_mask`
- `reconverge_pc`
- `path_kind`
- `source_branch_pc`

Stack operations:
- `push` on divergence when both taken and not-taken lane masks are non-empty.
- `restore` when the current path drains or reaches reconvergence.
- `pop` when the restored path completes.
- `clear` on wavefront retirement or fatal fault.

## Contract Boundaries

The architecture layer may decide whether the target design has:
- a branch-pending only model
- a one-level reconvergence stack
- a full nested reconvergence stack

It must not define RTL signal names or golden implementation code. Those are
owned by `gpgpu-golden` and `gpgpu-rtl`.

## Verification Hooks

Required evidence:
- dispatch allocation initializes PC, bases, wavefront identity, and EXEC mask
- branch changes PC and either updates EXEC or records a divergence stack entry
- special-state write changes EXEC/VCC/SCC in trace-visible form
- retired wavefront frees its resident slot and dispatch tag

## Do Not Copy From MIAOW

Do not copy MIAOW's 40 resident wavefront slots, 64-lane mask width, fixed PC
increment, Southern-Islands special-register numbers, or generated RTL style as
defaults. Copy the owner/consumer discipline and lifecycle visibility.
