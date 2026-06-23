# SIMT Golden Trace Spec

Golden SIMT traces must include:

- warp id;
- PC;
- active mask;
- reconvergence PC;
- call depth;
- divergence event;
- reconvergence event.

SIMT trace checks are independent from scoreboard dependency checks.

## XiangShan-Inspired State Blob Fields

`ARCHITECTURE_STATE_BLOB` must include per-warp PC, active mask,
reconvergence state, warp status, lane predicate state, and trap/fault state.
`GOLDEN_SIDECAR_STATE` may include scoreboard and outstanding memory state for
trace alignment, but SIMT correctness must compare only architecture-visible
state and events.
