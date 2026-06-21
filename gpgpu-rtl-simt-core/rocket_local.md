# Rocket Chip Local Reference For GPGPU RTL SIMT Core

This note expands the Rocket Chip references that matter for the `gpgpu-rtl-simt-core` skill. It focuses on typed params, optional-unit integration, ready-valid interfaces, RoCC command/response arbitration, HellaCache IO, local perf events, and the caveats for translating scalar CPU RTL patterns into SIMT RTL discipline.

Terminology note: Rocket Core is scalar in-order CPU RTL. Do not copy its pipeline as a SIMT scheduler. Preserve Rocket names only when discussing source. Translate the useful ideas to SIMT group lifecycle, active lane mask, scheduler, scoreboard, operand collection, FU/LSU ports, trace, and perf events.

## What Rocket Chip Teaches For This Skill

Rocket is useful for RTL integration patterns:

- typed params keep optional features and widths visible;
- optional units have decode/control, ports, response arbitration, busy/fault, and config hooks;
- ready-valid interfaces make backpressure explicit;
- local events are emitted near their owners;
- memory IO includes nack/replay/kill/ordered/status fields.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/rocket.md` | RTL SIMT lessons and seven-skill mapping. |
| `ref_submodule/rocket-chip/src/main/scala/tile/RocketTile.scala` | `RocketTileParams`, core/cache/RoCC/trace/interrupt integration. |
| `ref_submodule/rocket-chip/src/main/scala/tile/BaseTile.scala` | Tile boundary, params, hart ID, cache/MMU/PMP resource fields. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala` | Decode, hazards, CSR, optional FPU/RoCC/vector hooks, event sets. |
| `ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala` | Command router, response arbiter, busy/interrupt, memory/PTW ports. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala` | Ready-valid memory IO, nack/replay/ordered/store_pending/perf fields. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/Events.scala` | Event set and perf-counter organization. |

## Optional-Unit Pattern

`LazyRoCC.scala` shows optional accelerators connected through:

- `BuildRoCC` config entry;
- command and response bundles;
- command routing by opcode;
- response arbitration;
- memory/PTW/FPU optional ports;
- busy and interrupt signals;
- assertions that a command routes to at most one unit.

For SIMT RTL optional units such as tensor, special function, vector, atomic, or shared-memory extensions, require:

- config bit and typed params;
- decode and issue packet fields;
- scoreboard and operand effects;
- ready-valid backpressure;
- writeback arbitration;
- trace/perf events;
- tests and protocol checks.

## Ready-Valid And Memory IO

HellaCache IO makes memory backpressure and exceptional paths explicit: request ready, response valid, kill, s2_nack, raw hazard hint, replay_next, exceptions, ordered, store_pending, and perf.

Local SIMT core LSU interfaces should similarly expose:

- request accepted/not accepted;
- replay and nack cause;
- kill/flush/fence priority;
- response destination and active lane mask;
- store pending or outstanding memory status;
- counters near the LSU owner.

## Perf Events

Rocket Core and cache events count behavior near the pipeline/cache owners. For a SIMT core, emit events near:

- scheduler idle/stall;
- scoreboard wait;
- operand bank conflict;
- FU busy;
- branch/divergence;
- barrier wait;
- LSU replay/fault/cache miss;
- runtime queue admission.

## Caveats

- Do not copy Rocket's scalar fetch/decode/execute/writeback pipeline as SIMT.
- Do not map Rocket CSR/exception semantics directly to GPU completion/fault behavior.
- Do not confuse vector optional hooks with SIMT group execution.
- Use Rocket to structure interfaces and checks, not to define GPU execution semantics.
