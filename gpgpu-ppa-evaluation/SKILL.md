---
name: gpgpu-ppa-evaluation
description: Use when evaluating GPGPU performance, power, area, timing, energy, counters, bottlenecks, workload matrices, SAIF or VCD activity, synthesis reports, FPGA results, McPAT, GPUWattch, AccelWattch, or architecture tradeoffs.
---

# GPGPU PPA Evaluation

## Overview

Use this skill when a GPGPU change needs evidence beyond functional correctness. PPA conclusions must bind workload, backend, configuration, counters, activity, and reports into a controlled comparison.

## Core Rule

Do not claim a design is better without a baseline, variant, workload, configuration, backend, metric, evidence path, and interpretation. Classify the result before reporting it:

| Claim | Required evidence |
|---|---|
| optimization claim | controlled baseline and variant with one intended variable changed |
| credibility claim | working correctness path plus RTL, FPGA, synthesis, benchmark, or power/area evidence showing the prototype is real |
| exploratory observation | multiple variables changed or incomplete counters; label as hypothesis |

A credibility claim can cite ISA scope, benchmark capability, FPGA prototype data, and ASIC-style estimates, but it must also state relaxed design goals and comparison caveats.

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
- runtime launch latency, memory latency, interconnect/L2/DRAM queue pressure, and trace sampling scope when modeled

If counters are missing, state whether the conclusion is a hypothesis or measured fact.

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

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains synthesis reports, counters, backend evidence, and full-stack reproducibility for PPA work.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the MIAOW paper's FPGA, area, power, performance, OpenCL/Rodinia, and comparison evidence, plus the caveats that prevent overclaiming.

For deeper GPGPU-Sim background tied to this skill, read `gpgpusim_local.md` in this directory. It explains reproducible config records, runtime/cycle/memory counters, trace sampling, AerialVision, AccelWattch, and power-model caveats.
