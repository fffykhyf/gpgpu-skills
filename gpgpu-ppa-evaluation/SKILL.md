---
name: gpgpu-ppa-evaluation
description: Use when evaluating GPGPU performance, power, area, timing, energy, counters, bottlenecks, workload matrices, SAIF or VCD activity, synthesis reports, FPGA results, McPAT, GPUWattch, AccelWattch, or architecture tradeoffs.
---

# GPGPU PPA Evaluation

## Overview

Use this skill when a GPGPU change needs evidence beyond functional correctness. PPA conclusions must bind workload, backend, configuration, counters, activity, and reports into a controlled comparison. Use Rocket Chip as the reference for keeping named configs, local perf events, cache/memory counters, traces, regression flows, and generated hardware evidence tied together. Use XiangShan as the reference for HPM event ownership, TopDown bottleneck decomposition, checkpoint/SimPoint methodology, and careful separation between research prototype evidence and architecture claims.

## Core Rule

Do not claim a design is better without a baseline, variant, workload, configuration, backend, metric, evidence path, and interpretation. Classify the result before reporting it:

| Claim | Required evidence |
|---|---|
| optimization claim | controlled baseline and variant with one intended variable changed |
| credibility claim | working correctness path plus RTL, FPGA, synthesis, benchmark, or power/area evidence showing the prototype is real |
| exploratory observation | multiple variables changed or incomplete counters; label as hypothesis |

A credibility claim can cite ISA scope, benchmark capability, FPGA prototype data, and ASIC-style estimates, but it must also state relaxed design goals and comparison caveats.

Any PPA claim must also identify the generated configuration and instrumentation contract. If a change affects protocol widths, source IDs, cache/MSHR resources, optional units, runtime queues, or memory maps, the report must say which counters or traces prove that the configured hardware was the hardware evaluated.

## Terminology Contract

Use canonical terms in config IDs, counter names, and PPA tables. Keep source aliases only when reporting a specific backend counter.

| Canonical term | Source aliases | Evaluation meaning |
|---|---|---|
| SIMT group | warp, wavefront, wave | scheduling group counted for issue, stalls, occupancy, and launch shape |
| simt_group_id | warp ID, `wfid`, wave ID, wavefront tag | trace/counter identity when per-group data is reported |
| active lane mask | active mask, thread mask, `tmask`, `EXEC` mask | lane utilization and divergence evidence |
| CTA/workgroup | CTA, block, workgroup | workload launch unit and local-memory/barrier scope |
| compute core/CU | core, CU, compute unit | resource unit for area, power, counters, and occupancy |

## Minimum Evaluation Record

| Field | Required content |
|---|---|
| config_id | commit, build flags, compute core/CU, SIMT-group/thread, memory/cache, ISA/features |
| baseline | unchanged reference with exact command or report path |
| variant | changed design with one intended variable changed |
| workload | kernel or benchmark, input size, launch shape, memory image |
| backend | simulator, RTL sim, synthesis, FPGA, or analytic model |
| correctness | pass/fail, trace diff state, known limitations |
| counters | cycles, instrs, IPC, stalls, load/store, cache, memory |
| reports | area, timing, Fmax, power, SAIF/VCD, trace, visualization, or model output |
| interpretation | what the data supports and what it does not support |

If multiple variables changed, split the experiment or label the result as exploratory.

For generated designs, include the config fragment or option dump, derived topology summary, public capability/version output when present, and monitor status for the protocol under test.

## Correctness Before PPA

Use this order:

1. Correctness gate: smoke/regression/trace diff passes.
2. Performance gate: counters explain the observed speedup or slowdown.
3. Area/timing gate: synthesis or FPGA reports show resource and frequency impact.
4. Power/energy gate: vectorless or activity-annotated estimate is identified.

An incorrect design's IPC is not useful evidence.

## Counter Schema

Prefer adding counters before tuning:

- total cycles and committed instructions
- IPC and issued SIMT groups
- scheduler idle and active SIMT groups
- scoreboard, operand, ALU/FPU/LSU/SFU/TCU stalls
- branch and divergence counts
- load/store requests and latency
- coalescer misses or merge rate
- cache reads/writes, misses, bank stalls, MSHR stalls
- replay, nack, kill, flush, TLB miss, uncached/MMIO, source/tag exhaustion, and ordering/fence stalls when modeled
- runtime launch latency, command queue occupancy, completion latency, memory latency, interconnect/L2/DRAM queue pressure, and trace sampling scope when modeled

If counters are missing, state whether the conclusion is a hypothesis or measured fact.

## XiangShan HPM And TopDown Pattern

Use XiangShan as the reference for evidence that explains why a result changed:

| Evidence contract | XiangShan anchor | Local PPA rule |
|---|---|---|
| hardware event ownership | PDF HPM chapter, `PMParameters.scala` | Put counters near the module that owns the event, and document trigger conditions. |
| counter selection | `mhpmcounter3-31`, HPM event selectors | Keep event selection, grouping, privilege/sample domain, and overflow behavior reproducible. |
| top-down attribution | `TopDownGen.scala`, debugTopDown ports | Roll counters into bottleneck classes before claiming a specific optimization cause. |
| memory bottlenecks | LSU/DCache/MMU/CoupledL2 chapters | Separate replay, TLB miss, DCache miss, MSHR full, uncache/MMIO, L2, and protocol stalls. |
| workload sampling | NEMU checkpoint and SimPoint flow | Use checkpoints, sampled regions, and weights for long workloads instead of ad hoc partial runs. |
| artifact discipline | XiangShan MICRO methodology | Tie functional verification, debug traces, performance validation, and artifact provenance together. |

For local GPGPU work, translate frontend/backend/memory/cache into launch/dispatch, scheduler/issue, SIMT divergence, register/operand, LSU/coalescer, cache/TLB/NoC/DRAM, barrier, and atomic classes.

## Rocket Chip Evidence Pattern

Use Rocket Chip as the reference for placing evidence near the logic:

| Evidence | Rocket Chip anchor | Local rule |
|---|---|---|
| core events | `RocketCore` event sets | Count issue, stalls, replay, flush, branch/divergence, and unit interlocks at the owner module. |
| cache/memory events | `HellaCachePerfEvents`, DCache events | Count misses, grants/responses, blocked cycles, TLB misses, uncached/MMIO, and queue pressure in the memory path. |
| trace path | `trace/` encoder/controller/sink | Preserve trace configuration, sampling scope, and event schema with the report. |
| config comparison | named `Configs.scala` fragments | Compare named configs with one intended variable changed. |
| harness/regression | `TestHarness`, `regression/`, Verilator support | Record the correctness gate and backend used before interpreting counters. |

Borrow the evidence discipline, not Rocket's CPU-specific event meanings.

## GPGPU-Sim Evidence Loop

Use GPGPU-Sim as the reference for simulator-based evidence:

1. Record workload, input size, kernel name, launch shape, and runtime path.
2. Record config file path or digest.
3. Run correctness gate before reading performance.
4. Collect core counters: cycles, instructions, issue rate, active/idle SIMT groups, scheduler stalls.
5. Collect memory counters: load/store count, memory latency, cache hits/misses, MSHR stalls, ICNT/L2/DRAM pressure.
6. Capture trace samples only with documented component/core/memory-partition sampling.
7. If using AccelWattch or another power model, record model version, XML/config file, activity source, and calibration caveat.
8. Compare against a baseline with one intended variable changed.

Simulator counters can support architecture hypotheses and bottleneck analysis. They are not RTL timing closure or silicon power evidence by themselves.

## Power And Area Discipline

- Report target clock, tool, device or technology, and build flags.
- Distinguish vectorless power from SAIF/VCD-annotated power.
- Keep SAIF/VCD tied to the workload that produced it.
- Record WNS and estimated Fmax, not only "timing passed".
- Preserve hierarchical area and power when the change is localized.
- When comparing to a commercial GPU or paper number, state process node, clock, CU count, memory system, compiler/runtime path, workload, estimation method, and which goals were relaxed. Do not imply PPA optimality from a research prototype credibility number.

## Common Mistakes

- Reporting speedup without cycle and stall breakdown.
- Comparing different configs or workloads and calling it an architecture win.
- Treating simulator counters as silicon timing or power without caveats.
- Using SAIF/VCD from a different workload or config.
- Reporting AccelWattch, McPAT, or GPUWattch output without model version, config, activity source, and calibration status.
- Keeping only summary numbers and losing the command or report path.
- Adding counters far from the event owner, making them impossible to reconcile with trace or RTL behavior.
- Comparing generated variants without recording the config fragment, derived topology, and protocol monitor status.
- Claiming a XiangShan-style top-down bottleneck without showing the counter owner, workload sample, config, and correctness gate behind it.

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains synthesis reports, counters, backend evidence, and full-stack reproducibility for PPA work.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the MIAOW paper's FPGA, area, power, performance, OpenCL/Rodinia, and comparison evidence, plus the caveats that prevent overclaiming.

For deeper GPGPU-Sim background tied to this skill, read `gpgpusim_local.md` in this directory. It explains reproducible config records, runtime/cycle/memory counters, trace sampling, AerialVision, AccelWattch, and power-model caveats.

For deeper Rocket Chip background tied to this skill, read `rocket_local.md` in this directory. It explains local perf events, HellaCache counters, trace infrastructure, named configs, TestHarness/regression/Verilator support, and how to bind PPA evidence to config and workload.

For XiangShan background tied to this skill, read `xiangshan_local.md` in this directory. It explains HPM/TopDown counters, backend and memory event ownership, NEMU instruction/profiling support, checkpoint/SimPoint flow, and how to adapt those evidence patterns to GPGPU PPA evaluation.
