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
