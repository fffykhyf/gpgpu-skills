# Vortex Local Reference For RTL SIMT Core

This note expands the Vortex references that matter for the
`gpgpu-rtl-simt-core` skill. It focuses on SIMT core state, RTL pipeline
boundaries, scheduler/issue/writeback behavior, and the simulator mirrors that
make RTL debug practical.

## What Vortex Teaches For This Skill

Vortex makes SIMT state explicit. Warp PC, active mask, stalled/active warp
sets, packet markers, scoreboard reservations, CTA state, and writeback release
rules are not incidental wires. They are architectural or microarchitectural
contracts that should be visible in RTL, simulator, and trace.

For this project, transfer these habits:

- define warp lifecycle before changing scheduler logic;
- keep schedule, fetch, decode, issue, operands, dispatch, execute, and commit
  responsibilities separable;
- keep scoreboard ownership out of operand read side effects;
- make branch/divergence/barrier/CTA state observable;
- use simulator trace alignment before relying only on waveforms.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/vortex.md` | Local extraction of Vortex SIMT lessons and how they map to skills. |
| `ref_submodule/vortex/docs/microarchitecture.md` | Threads, warps, active masks, `TMC`, `WSPAWN`, `SPLIT`, `JOIN`, `PRED`, `BAR`, and the pipeline. |
| `ref_submodule/vortex/docs/designs/cta_clustering_and_dispatch.md` | CTA-to-warp dispatch, CTA rank/size, cluster dimensions, and scheduler-visible launch state. |
| `ref_submodule/vortex/docs/designs/simx_simulator_architecture.md` | Simulator mirror for scheduler, decoder, scoreboard, operands, dispatcher, and functional units. |
| `ref_submodule/vortex/docs/debugging.md` | Trace-first RTL debug and SimX/RTL comparison workflow. |

## RTL Core Top-Level Boundary

`ref_submodule/vortex/hw/rtl/core/VX_core.sv` is the top-level RTL reference.
It wires the core pipeline and exposes the contract to the rest of the GPU.

Useful boundaries to notice:

- core identity and configuration are parameters or generated macros, not
  hidden constants;
- instruction fetch and data memory go through explicit memory/cache/MMU-facing
  interfaces;
- CTA dispatch and scheduler state meet at named interfaces rather than a
  testbench-only launch poke;
- LSU, FPU, SFU, TCU, and ALU units are separate execute paths behind dispatch;
- performance counters and debug traces are close to the pipeline events they
  measure.

When building a smaller core, you can collapse modules, but do not collapse the
contracts. The design should still be able to answer: who owns PC, who owns the
active mask, who can stall a warp, who reserves writeback, and who releases it.

## Scheduler And Warp Lifecycle

`ref_submodule/vortex/hw/rtl/core/VX_scheduler.sv` and the SimX mirror
`ref_submodule/vortex/sim/simx/scheduler.cpp` show the same core idea from RTL
and simulator sides.

State categories worth copying:

- active warp set;
- stalled or waiting warp set;
- per-warp PC;
- per-warp active mask;
- per-warp CTA/kernel state;
- branch/divergence/reconvergence state;
- barrier or CTA completion state;
- next-state update rules for suspend/resume.

SimX `Scheduler::schedule()` is a compact reference for correct sequencing:
CTA dispatch can activate a warp, `wspawn` can add warps, a ready warp is
selected, trace identity is allocated, and the warp is suspended until later
pipeline stages resume it. That separation prevents a warp from being issued
twice in the same cycle after a same-cycle resume.

For local RTL, write down the lifecycle states before editing scheduler logic:
inactive, ready, issued/waiting, waiting on scoreboard/operands/FU/memory,
barrier-stalled, CTA-reused, and done. Missing states usually become implicit
bugs in valid-ready logic.

## Fetch, Decode, Issue, And Commit Shape

Vortex keeps the common SIMT pipeline stages visible:

- `VX_fetch.sv`: instruction request path and per-warp fetch state.
- `VX_decode.sv`: raw instruction to decoded control.
- `VX_issue.sv`: decoded instruction buffering, slot selection, hazard checks,
  and dispatch eligibility.
- `VX_execute.sv`: routes work to functional units.
- `VX_commit.sv`: receives unit results, arbitrates writeback, releases
  scoreboard state, updates PC/control side effects, and emits debug trace.

The skill-level rule is that these responsibilities should not be hidden in one
large always block. A small project can implement fewer files, but the trace
and comments should preserve these conceptual stages.

## Issue Slice And Scoreboard Details

`ref_submodule/vortex/hw/rtl/core/VX_issue_slice.sv` is a useful slice-level
composition reference. It wires:

- `VX_ibuffer` for decoded instruction buffering;
- `VX_scoreboard` for dependency and structural hazard checks;
- `VX_operands` for register operand reads;
- `VX_dispatcher` for sending the issue packet to the selected FU.

The slice exposes `warp_issued`, and under scope/debug it taps decode,
operands, and writeback events. That is the right mindset: issue is not just
"send valid if ready"; it is also the place where stall attribution should be
visible enough for PPA and debug.

`ref_submodule/vortex/hw/rtl/core/VX_scoreboard.sv` is the main hazard
reference. Important behavior:

- it tracks in-use integer/floating/vector destination registers per warp;
- it reserves writeback destinations when an instruction leaves staging;
- it releases reservations on writeback, using EOP to avoid freeing too early
  for multi-packet instructions;
- it blocks on busy source or destination registers;
- it models FU locks/blocks and uses arbitration for issue selection;
- it has simulation assertions for invalid writeback and timeout-like bugs;
- it exports performance stall information.

For local RTL, define exactly when a destination is reserved, when it is freed,
whether a multi-packet operation frees on SOP or EOP, and how flush/kill/reset
interacts with outstanding reservations. Do this before adding more issue width.

## SIMT Control: Split/Join, TMC, WSPAWN, Barrier

The Vortex microarchitecture docs describe the SIMT control instructions:

- `TMC` changes the active thread mask.
- `WSPAWN` activates additional warps at a target PC.
- `SPLIT` and `JOIN` maintain divergent branch/reconvergence state.
- `PRED` handles predicate-like mask behavior.
- `BAR` interacts with the barrier unit and warp scheduler.

The RTL source map for these concepts includes:

- `ref_submodule/vortex/hw/rtl/core/VX_split_join.sv`
- `ref_submodule/vortex/hw/rtl/core/VX_ipdom_stack.sv`
- `ref_submodule/vortex/hw/rtl/core/VX_wctl_unit.sv`
- `ref_submodule/vortex/hw/rtl/core/VX_bar_unit.sv`

Do not treat divergence as a hidden branch side effect. A local design needs an
explicit place for active-mask update, reconvergence target, stack push/pop, and
warp wakeup. If the first implementation is simplified, document the missing
cases rather than leaving them as unspecified behavior.

## CTA Dispatch And KMU Boundary

Vortex's launch path reaches the core through a KMU/CTA boundary:

- `ref_submodule/vortex/hw/rtl/VX_kmu.sv` owns kernel-management state from DCR
  programming: startup PC, kernel entry, args pointer, grid/block dimensions,
  local memory size, block size, warp step, and cluster dimensions.
- `ref_submodule/vortex/hw/rtl/core/VX_cta_dispatch.sv` presents warp records to
  the core scheduler, including CTA id/rank/size, thread and block indices, and
  per-CTA entry/argument state.
- SimX mirrors this in `sim/simx/scheduler.cpp`, where `activate_warp()` copies
  CTA metadata into warp-visible CSR state.

For this skill, the key point is that CTA state is not testbench decoration. It
affects CSRs, per-thread IDs, local memory addressing, kernel entry, and warp
reuse. Keep the boundary explicit even in a minimal runtime.

## Commit And Writeback Contract

`ref_submodule/vortex/hw/rtl/core/VX_commit.sv` is the reference for the final
architectural effect stage. The specific module is larger than most local needs,
but the contract is general:

- arbitrate results from multiple functional units;
- apply writeback only under the active mask and writeback enable;
- preserve destination register type and byte-selection rules;
- update scoreboard release state at the same architectural completion point;
- handle PC/control side effects from branch/control instructions;
- emit a trace row that includes PC, warp, mask, destination, data, FU/op type,
  SOP/EOP, and UUID-like identity.

The common bug to avoid is releasing scoreboard state when a response packet
arrives instead of when the instruction's architectural writeback is complete.

## Simulator Twin References

Use these SimX files to understand the expected behavior behind RTL changes:

- `ref_submodule/vortex/sim/simx/scheduler.cpp`: warp lifecycle, CTA activation,
  PC, active masks, suspend/resume.
- `ref_submodule/vortex/sim/simx/instr_trace.h`: trace identity and fields.
- `ref_submodule/vortex/sim/simx/core.cpp`: module graph and core pipeline.
- `ref_submodule/vortex/sim/simx/scoreboard.cpp`: software mirror of hazard
  ownership.
- `ref_submodule/vortex/sim/simx/operands.cpp` and `opc_unit.cpp`: operand and
  register-file semantics.
- `ref_submodule/vortex/sim/simx/*_unit.cpp`: functional unit semantics.

When RTL and simulator disagree, align on a trace row first. A waveform without
the matching scheduler/scoreboard/commit trace usually takes longer to debug.

## Local Transfer Checklist

- Before changing scheduler RTL, list the warp lifecycle states and legal
  transitions.
- Before adding an instruction, list its impact on PC, active mask, scoreboard,
  register writeback, memory, barrier, CSR, and CTA-visible state.
- Before widening issue, define arbitration, FU locks, scoreboard conflicts,
  and writeback conflicts.
- Before adding divergence, define reconvergence stack behavior and trace fields.
- Before adding barrier or CTA dispatch, define wakeup/completion semantics.
- For every RTL behavior change, update or identify the simulator/golden trace
  owner that can confirm it.

## What Not To Copy

- Do not import Vortex's full extension set just because the source exists.
- Do not copy Vortex pipeline depth if a smaller design can preserve the same
  visible contracts.
- Do not implement scoreboard behavior in operand read logic.
- Do not let active mask or PC become temporary combinational helper signals.
- Do not claim correctness from waveform inspection without a reproducible trace
  or regression.
