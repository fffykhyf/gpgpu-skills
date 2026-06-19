# XiangShan Local Reference For GPGPU PPA Evaluation

This note expands the XiangShan references that matter for the `gpgpu-ppa-evaluation` skill. It focuses on HPM event ownership, TopDown bottleneck decomposition, backend/memory counter placement, NEMU profiling, checkpoint/SimPoint methodology, and artifact discipline.

Terminology note: XiangShan HPM categories are CPU-oriented. Preserve names such as frontend, backend, memory, cache, CSR, HPM, and TopDown when discussing the source. For local GPGPU PPA, map them to launch/dispatch, scheduler/issue, SIMT divergence, register/operand, LSU/coalescer, cache/TLB/NoC/DRAM, barrier, atomic, runtime queue, and completion categories.

## What XiangShan Teaches For This Skill

XiangShan's PPA lesson is that performance evidence must be owned, classifiable, and reproducible. The PDF HPM chapter and backend TopDown code show counters close to event owners and a top-down hierarchy that explains why cycles were lost.

For local GPGPU work, borrow:

- counter ownership near the module that creates the event;
- event selectors and reproducible sampling configuration;
- top-down bottleneck classes;
- memory replay/cache/TLB/L2 counters;
- checkpoint or sampled-region flow for long workloads;
- explicit artifact provenance before claims.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/xiangshan.md` | PPA lessons and seven-skill mapping. |
| `ref/xiangshan.pdf` | HPM chapter, backend/memory/cache event descriptions, TopDown PMU discussion. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/PMParameters.scala` | Performance monitor parameter surface. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/TopDownGen.scala` | TopDown event generation and backend attribution. |
| `ref_submodule/xiangshan/src/main/scala/top/BusPerfMonitor.scala` | Bus/perf monitor integration. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/XSCore.scala` | Perf event wiring from frontend, backend, LSU, cache hierarchy. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/lsqueue/LoadQueueReplay.scala` | Replay counters and over-threshold replay counters. |
| `ref_submodule/xiangshan-nemu/src/cpu/cpu-exec.c` | Instruction counting, execution statistics, simulation frequency. |
| `ref_submodule/xiangshan-nemu/src/checkpoint/` | Checkpoint, SimPoint, semantic point flow for representative runs. |

## HPM Event Ownership

The PDF describes HPM with hardware counters and event selectors. Events are grouped across frontend, backend, memory, and cache, and selectors can combine multiple events and sampling contexts.

Local GPGPU rule:

- every counter must name the module owner;
- every counter must define its trigger condition;
- every counter must state whether it is architectural, microarchitectural, simulator-only, or debug-only;
- report config and sampling mode with the data.

## TopDown Translation

XiangShan's TopDown infrastructure is CPU-specific, but the structure is useful:

- start with broad bottleneck classes;
- drill down to owner counters;
- avoid claiming the lowest-level cause without evidence for higher-level attribution.

For GPGPU, use classes such as:

- launch/runtime overhead;
- scheduler empty or scoreboard blocked;
- SIMT divergence and inactive lanes;
- operand/register-bank pressure;
- FU utilization;
- LSU/coalescer replay;
- shared-memory bank conflict;
- TLB/cache/MSHR stalls;
- NoC/L2/DRAM pressure;
- barrier/atomic serialization.

## Memory Counters

`LoadQueueReplay.scala` includes counters for TLB miss, memory ambiguity, nuke, RAR/RAW reject, bank conflict, DCache replay, forward fail, DCache miss, multi-match, and over-threshold replay behavior.

For local PPA, avoid one generic `memory_stall`. Separate:

- coalescer retries;
- lane mask waste;
- shared-memory conflicts;
- TLB misses;
- cache misses;
- MSHR full;
- NoC/L2/DRAM queues;
- uncache/MMIO;
- atomic/fence/order stalls;
- replay count and replay cycles.

## NEMU Profiling And Checkpoints

`cpu-exec.c` tracks guest instruction counts and simulation statistics. The NEMU README and checkpoint sources describe SimPoint/checkpoint flows. For GPGPU PPA, this becomes a rule for long workloads:

- record full workload and sampled region separately;
- preserve sample weights;
- keep checkpoint, config, memory image, and launch descriptor together;
- do not compare sampled and full-run results without labeling the difference.

## Artifact Record

Before reporting a PPA conclusion inspired by XiangShan discipline, record:

- commit and config name/digest;
- workload, input, launch shape, and backend;
- correctness gate;
- counter list and owners;
- trace/perf command;
- synthesis/FPGA/power report paths when used;
- relaxed goals and caveats.

## Caveats

- Do not copy XiangShan counter names as GPU counter names without remapping.
- Do not treat CPU HPM events as GPU bottleneck classes.
- Do not claim silicon PPA from simulator-only counters.
- Do not use checkpointed or sampled results without recording sample identity and weight.
