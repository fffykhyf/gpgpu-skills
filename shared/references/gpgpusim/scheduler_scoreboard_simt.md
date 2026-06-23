# Scheduler, Scoreboard, and SIMT Rules

SM issue gate:

1. warp valid and not exited;
2. not waiting at barrier, membar, atomic, or depbar-equivalent state;
3. ibuffer has an instruction;
4. SIMT top PC matches instruction PC;
5. scoreboard reports no source, destination, predicate, or address collision;
6. target pipe has a free slot;
7. dual-issue policy allows the second issue;
8. issue and reserve scoreboard destinations.

Non-issue reasons must be mutually attributable:

- `idle_control`
- `ibuffer_empty`
- `simt_redirect`
- `scoreboard_wait`
- `pipe_unavailable`
- `barrier_wait`
- `membar_wait`
- `atomic_wait`
- `memory_backpressure`

State split:

- SIMT owns PC, active mask, reconvergence PC, call depth, and divergence event.
- Scoreboard owns pending destination registers, long-op destination registers,
  reserve/release events, and collision result.

Raw basis:

- `raw/gpgpu-sim-shader-core-and-warp-scheduler-notes.md`
- `raw/gpgpu-sim-scoreboard-and-simt-stack-notes.md`

