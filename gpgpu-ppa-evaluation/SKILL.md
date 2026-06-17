---
name: gpgpu-ppa-evaluation
description: Use when evaluating GPGPU performance, power, area, timing, energy, counters, bottlenecks, synthesis reports, FPGA results, McPAT, GPUWattch, AccelWattch, or architecture tradeoffs.
---

# GPGPU PPA Evaluation

## Overview

Use this skill when a GPGPU change needs evidence beyond functional correctness. PPA work must tie performance, power, area, and timing claims to counters, reports, and controlled comparisons.

## Core Rule

Do not claim an optimization is better without a baseline, workload, configuration, metric, and reproducible command or report path.

## Minimum Evaluation Record

For every result, capture:

| Item | Required content |
|---|---|
| Baseline | commit/config/parameter set before the change |
| Variant | commit/config/parameter set after the change |
| Workload | program, input size, launch config, memory image |
| Backend | simulator, RTL sim, FPGA, synthesis, or analytic model |
| Metrics | cycles, IPC, stalls, bandwidth, power, area, timing, or energy |
| Evidence | log path, trace path, report path, or command |
| Interpretation | what changed and what remains uncertain |

## Counter First

Prefer adding counters before making performance decisions:

- total cycles
- committed instructions
- IPC
- issued warps
- scoreboard stalls
- memory stalls
- barrier stalls
- load/store request count
- coalesced request count
- cache hits/misses when cache exists

If counters are missing, state whether the current conclusion is a hypothesis or measured fact.

## PPA Workflow

1. Define the hypothesis and the bottleneck.
2. Choose the smallest benchmark that exercises the bottleneck.
3. Run the baseline and save logs.
4. Run the variant under the same configuration.
5. Compare counters before inspecting aggregate speedup.
6. For power or area, map simulator/RTL activity to McPAT, GPUWattch, AccelWattch, or synthesis reports.
7. Report regressions and measurement limits with the result.

## Common Mistakes

- Reporting speedup without showing cycle and stall breakdown.
- Comparing different configs or workloads and calling it an architectural win.
- Treating simulator counters as silicon timing or power without caveats.
- Optimizing for IPC while ignoring bandwidth, energy, or area.
- Keeping only summary numbers and losing the report path needed to reproduce them.
