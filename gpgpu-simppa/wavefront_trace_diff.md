# Wavefront Trace Diff

This file upgrades differential comparison from raw instruction trace diff to
wavefront state and EXEC-mask aware comparison.

## Diff Granularity

instruction trace diff is insufficient.

Required diff layers:
- PC diff
- decoded instruction record diff
- EXEC mask diff
- VCC/SCC special-state diff
- wave state diff
- divergence path diff
- memory bundle diff
- coalesced transaction diff
- side-effect event diff

## EXEC mask diff

EXEC mask diff must report:
- `cu_id`
- `wavefront_id`
- `pc`
- expected mask
- actual mask
- producer event
- consumer event
- affected lanes
- dependent instruction or memory bundle

## Wave state diff

wave state diff must compare:
- `ACTIVE`
- `PENDING`
- `STALLED`
- `WAITING_MEMORY`
- `DIVERGED`
- `RECONVERGING`
- `RETIRED`

The report must include owner module and release condition for the mismatched
state.

## Divergence path diff

divergence path diff must compare:
- branch condition source
- taken mask
- not-taken mask
- selected path order
- reconvergence stack entries
- restored PC
- restored EXEC mask

## First Divergence Rule

The first divergence must be the earliest deterministic architectural mismatch,
not the final memory dump symptom. Memory mismatches must route back to the
memory bundle, coalescer, LDS/global space tag, atomic/fence, or writeback event
that first diverged.

## Required Outputs

AI-facing reports:
- `FIRST_DIVERGENCE_REPORT`
- `NORMALIZED_TRACE_IR`
- `ROOT_CAUSE_REPORT`
- `PERF_ATTRIBUTION_GRAPH`

Human-facing reports:
- `DEBUG_SUMMARY.zh.md`
- `PATCH_CARD.zh.md` through `gpgpu-loop`

## Failure Routing

Route:
- EXEC/mask mismatch -> `gpgpu-golden` or `gpgpu-rtl`
- memory bundle mismatch -> `gpgpu-runtime` or `gpgpu-rtl`
- coalescing mismatch -> `gpgpu-runtime`, `gpgpu-rtl`, or `gpgpu-memory`
- cross-CU ordering mismatch -> `gpgpu-interconnect`, `gpgpu-memory`, or `gpgpu-atomic-sync`
