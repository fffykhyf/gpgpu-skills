# GPGPU-Sim Scoreboard And SIMT Stack Notes

Source repo: `ref_submodule/gpgpu-sim`

Primary files:

- `src/gpgpu-sim/scoreboard.{h,cc}`
- `src/abstract_hardware_model.{h,cc}`
- `src/gpgpu-sim/shader.{h,cc}`

## Scoreboard Mechanism

Owner:

- `Scoreboard` in `src/gpgpu-sim/scoreboard.*`

State:

- `reg_table[warp_id]`: pending destination registers per warp.
- `longopregs[warp_id]`: destination registers of long-latency load-like operations.
- shader id and pointer to GPU context for tracing/debug.

Events:

- `reserveRegisters(inst)` reserves all `inst->out[]` registers at issue.
- loads from global/local/param/texture spaces mark outputs as long ops.
- `checkCollision(wid, inst)` checks all output, input, predicate, and address registers against pending writes.
- `releaseRegisters(inst)` releases outputs at writeback/completion.
- `pendingWrites(wid)` reports whether a warp still has outstanding destinations.

Hardware behavior modeled:

- RAW/WAW hazard avoidance under in-order issue.
- Long-latency memory destination tracking.
- Membar and warp-wait behavior can query pending writes.

Simulator-only assumptions:

- register sets are C++ sets;
- there is no explicit ready timestamp or bypass model in the scoreboard itself;
- no WAR check because issue is modeled in order.

RTL contract candidate:

- per-warp pending destination bitset or CAM;
- reserve at issue;
- release on writeback or memory fill;
- issue blocked if any source/destination/predicate/address register collides with pending destinations.

## SIMT Stack Mechanism

Owner:

- `simt_stack` in `src/abstract_hardware_model.*`

State:

- per-warp stack entries:
  - `m_pc`
  - `m_active_mask`
  - `m_recvg_pc`
  - `m_calldepth`
  - `m_branch_div_cycle`
  - entry type: normal or call

Events:

- `launch(start_pc, active_mask)` initializes warp execution.
- `get_active_mask()` feeds scheduler issue.
- `get_pdom_stack_top_info()` exposes current PC and reconvergence PC.
- `update(thread_done, next_pc, recvg_pc, next_inst_op, next_inst_size, next_inst_pc)` performs divergence/reconvergence update.

Hardware behavior modeled:

- active-lane mask selection per issued instruction;
- divergent path tracking;
- reconvergence PC;
- call/return depth handling.

Simulator-only assumptions:

- implementation follows GPGPU-Sim's pdom-style stack and NVIDIA/PTX control-flow assumptions;
- exact stack container and update order should not be copied mechanically.

RTL contract candidate:

- each warp must expose current PC, active mask, reconvergence metadata, and branch/divergence event for tracing;
- scheduler must fetch issue PC from the SIMT control state, not only from ibuffer;
- PC mismatch must flush stale ibuffer state or equivalent.

## Membar, Barrier, Atomic Waiting

Observed in `src/gpgpu-sim/shader.cc`:

- `BARRIER_OP` records the last instruction and calls barrier-set logic.
- `MEMORY_BARRIER_OP` sets warp membar state.
- `shd_warp_t::waiting()` stalls warps at barrier, membar, atomic, and depbar-like states.
- membar waiting checks pending scoreboard writes and may invalidate L1; the reader pass found a TODO for a large fixed membar stall, so this is not hardware-clean.
- shared atomics execute at writeback; global atomics execute on memory return through `mem_fetch::do_atomic()`.

Design implication:

- atomics/fences/barriers need a separate design rule instead of being hidden under generic scoreboard waits.

## Counters / Evidence Hooks

Useful counters/events:

- `shader_cycle_distro[1]` for scoreboard wait.
- warp divergence visualizer fields: `WarpDivergenceBreakdown`, `shaderwarpdiv`.
- barrier/membar waiting is not cleanly represented as a first-class stall taxonomy in the files read; future skill patches should add one if simple-gpgpu needs precise synchronization attribution.

## Design Rule

Rule name: SIMT and scoreboard are separate contracts

Problem solved: avoids mixing control divergence with data hazards.

Required state contract:

- SIMT stack: PC, active mask, reconvergence PC, call depth.
- Scoreboard: pending destination registers, long-op destination marks, release source.

Required counter/stall reason:

- scoreboard wait;
- control hazard / SIMT redirect;
- barrier wait;
- membar wait;
- atomic wait.

Applicable skill:

- `gpgpu-arch`
- `gpgpu-rtl`
- `gpgpu-simppa`
- `gpgpu-golden`

Implementation anchor:

- `src/abstract_hardware_model.h:simt_stack`
- `src/gpgpu-sim/scoreboard.cc`
- `src/gpgpu-sim/shader.cc:scheduler_unit::cycle`
- `src/gpgpu-sim/shader.cc:shader_core_ctx::issue_warp`
