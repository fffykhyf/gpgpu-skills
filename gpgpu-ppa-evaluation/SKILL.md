---
name: gpgpu-ppa-evaluation
description: Use when evaluating GPGPU performance, power, area, timing, energy, counters, bottlenecks, workload matrices, SAIF or VCD activity, synthesis reports, FPGA results, McPAT, GPUWattch, AccelWattch, or architecture tradeoffs.
---

# GPGPU PPA Evaluation

## Overview

Use this skill when a GPGPU change needs evidence beyond functional correctness. PPA conclusions must bind workload, backend, configuration, counters, activity, and reports into a controlled comparison.

## Core Rule

Do not claim a design is better without a baseline, variant, workload, configuration, backend, metric, evidence path, and interpretation.

## Minimum Evaluation Record

| Field | Required content |
|---|---|
| config_id | commit, build flags, core/warp/thread, memory/cache, ISA/features |
| baseline | unchanged reference with exact command or report path |
| variant | changed design with one intended variable changed |
| workload | kernel or benchmark, input size, launch shape, memory image |
| backend | simulator, RTL sim, synthesis, FPGA, or analytic model |
| correctness | pass/fail, trace diff state, known limitations |
| counters | cycles, instrs, IPC, stalls, load/store, cache, memory |
| reports | area, timing, Fmax, power, SAIF/VCD, or model output |
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
- IPC and issued warps
- scheduler idle and active warps
- scoreboard, operand, ALU/FPU/LSU/SFU/TCU stalls
- branch and divergence counts
- load/store requests and latency
- coalescer misses or merge rate
- cache reads/writes, misses, bank stalls, MSHR stalls

If counters are missing, state whether the conclusion is a hypothesis or measured fact.

## Power And Area Discipline

- Report target clock, tool, device or technology, and build flags.
- Distinguish vectorless power from SAIF/VCD-annotated power.
- Keep SAIF/VCD tied to the workload that produced it.
- Record WNS and estimated Fmax, not only "timing passed".
- Preserve hierarchical area and power when the change is localized.

## Common Mistakes

- Reporting speedup without cycle and stall breakdown.
- Comparing different configs or workloads and calling it an architecture win.
- Treating simulator counters as silicon timing or power without caveats.
- Using SAIF/VCD from a different workload or config.
- Keeping only summary numbers and losing the command or report path.

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It summarizes the relevant Vortex design documents and code paths so routine PPA work does not require re-reading the whole reference tree.
