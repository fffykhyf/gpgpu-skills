# Rocket Chip Local Reference For GPGPU PPA Evaluation

This note expands the Rocket Chip references that matter for the `gpgpu-ppa-evaluation` skill. It focuses on local event counters, cache/memory perf events, trace infrastructure, named configs, TestHarness/regression/Verilator support, and binding PPA evidence to workload and configuration.

Terminology note: Rocket counters are CPU/SoC counters. Preserve Rocket names only when discussing source. For local GPGPU evaluation, translate event ownership to scheduler, SIMT group, active lane mask, scoreboard, operand, FU, LSU/coalescer, cache/TLB/NoC/DRAM, runtime queue, and completion categories.

## What Rocket Chip Teaches For This Skill

Rocket's PPA lesson is evidence discipline:

- performance events live near owner logic;
- cache/memory paths expose detailed counters;
- traces and harnesses make runs reproducible;
- named configs allow controlled comparisons;
- regression and emulator support keep evidence tied to a backend.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/rocket.md` | PPA lessons and seven-skill mapping. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala` | Event sets around core behavior, stalls, replays, flushes, cache/TLB events. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/Events.scala` | Event-set and counter organization. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala` | `HellaCachePerfEvents`: acquire, release, grant, TLB miss, blocked, canAcceptStore. |
| `ref_submodule/rocket-chip/src/main/scala/trace/` | Trace encoder/controller/sink/arbiter/monitor infrastructure. |
| `ref_submodule/rocket-chip/src/main/scala/system/TestHarness.scala` | Backend harness and success/debug wiring. |
| `ref_submodule/rocket-chip/regression/` | Regression suite organization. |
| `ref_submodule/rocket-chip/src/main/resources/csrc/` | Verilator emulator support, SimJTAG/SimDTM/remote bitbang style collateral. |
| `ref_submodule/rocket-chip/src/main/scala/system/Configs.scala` | Named configs for controlled comparisons. |

## Counter Placement

Rocket places events near the core and cache behavior being measured. For local GPGPU PPA, require counter owner and trigger conditions for:

- scheduler idle and eligible SIMT groups;
- issue count and active lane utilization;
- scoreboard/operand stalls;
- FU utilization;
- branch divergence and reconvergence;
- barrier waits;
- LSU/coalescer replay;
- cache/TLB/MSHR/NoC/DRAM stalls;
- runtime queue and launch/completion latency.

## Trace And Harness Evidence

Rocket's trace and harness infrastructure reinforce that a PPA report needs reproducible context. Local reports should record:

- config name or digest;
- commit;
- workload and launch shape;
- backend: simulator, RTL sim, FPGA, synthesis, or model;
- correctness gate;
- trace/counter command;
- area/timing/power report path when relevant.

## Config-Controlled Comparisons

Rocket uses named configs for variants. Local GPGPU evaluation should compare variants with one intended variable changed. If multiple variables changed, label the result exploratory.

## Caveats

- Rocket CPU events are not GPU bottleneck classes.
- Simulator counters are not silicon timing or power evidence.
- Trace samples must be tied to workload and config.
- Do not claim PPA improvement without correctness, counter definitions, and environment provenance.
