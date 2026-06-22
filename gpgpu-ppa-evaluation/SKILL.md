---
name: gpgpu-ppa-evaluation
description: Use when evaluating GPGPU performance, power, area, timing, energy, counters, bottlenecks, workload matrices, SAIF or VCD activity, synthesis reports, FPGA results, McPAT, GPUWattch, AccelWattch, or architecture tradeoffs.
---

# GPGPU PPA Evidence Compiler Skill

## 1. Objective

Compile verified traces, counters, reports, and workload metadata into controlled performance, power, and area claims with causal feedback to architecture, config, RTL, memory, or runtime.

## 2. Input Contract

Input is an evaluation intent with baseline candidate, variant candidate, workload, backend, config digest, correctness gate, metric target, and expected feedback owner.

## 3. PPA State Model

PPA evidence must preserve the GPU state that caused the metric:

| Evidence state | Required binding |
|---|---|
| launch state | kernel image, args, grid/block shape, queue timeline, launch latency |
| compute state | PC/mask/register effects, issued SIMT groups, occupancy, divergence |
| dependency state | scoreboard stalls, operand stalls, replay, barrier, hazard graph counters |
| memory state | load/store count, coalescing, cache hits/misses, MSHR, bank, NoC/L2/DRAM pressure |
| pipeline state | fetch/decode/issue/execute/writeback utilization and stalls |
| config state | source config, derived topology, ABI version, backend, commit/report path |
| physical state | area hierarchy, timing/Fmax/WNS, power/energy, activity source |

## 4. Mandatory Five Questions

For every PPA claim answer:

1. What state exists? Name workload, config, launch, compute, memory, dependency, pipeline, or physical state.
2. Who produces it? Trace, counter owner, synthesis tool, power model, runtime, or benchmark harness.
3. Who consumes it? Architecture decision, config update, RTL/memory/runtime feedback, or report.
4. How does it change? Define baseline-to-variant controlled diff and causal path.
5. How do we verify it? Name correctness gate, counter audit, report provenance, and reproducibility command.

## 5. Baseline Definition

Baseline must be strict:

- exact commit and config digest.
- backend: golden sim, RTL sim, FPGA, synthesis, analytic model, or power model.
- workload and input size.
- launch shape and runtime path.
- correctness status and trace/regression gate.
- metric collection commands and report paths.
- known limitations and unsupported features.

No baseline means no improvement claim.

## 6. Variant Definition

Variant must be a controlled diff:

- one intended architecture/config/RTL/memory/runtime variable changed.
- all unrelated config, workload, tool, and backend inputs held constant.
- generated topology summary recorded.
- monitor/assertion status preserved.
- if multiple variables changed, label result exploratory and split follow-up experiments.

## 7. Workload Model

A workload record must contain:

- kernel or benchmark name and version.
- input data, memory image, and random seeds.
- launch dimensions and local/shared memory.
- runtime queue/event/fence path.
- warmup, sampling, checkpoint, or region selection.
- correctness oracle and expected output/trace status.

## 8. Metric Model

| Metric class | Required fields |
|---|---|
| latency | total cycles/time, launch latency, kernel cycles, memory latency, queue wait |
| throughput | IPC, issued SIMT groups, active lanes, occupancy, memory bandwidth |
| energy | power model, activity source, duration, dynamic/static split, calibration caveat |
| area | hierarchy, technology/device, resource type, generated features, utilization |
| timing | target clock, achieved Fmax, WNS/TNS, critical path owner, constraints |

Counters must name producer modules, trigger conditions, and reset/sample windows.

## 9. Transformation Rules: Causal Attribution Engine

Attribute performance changes into controlled buckets:

| Bucket | Evidence required |
|---|---|
| scheduler gain | fewer scheduler idle cycles, higher ready SIMT groups, lower scoreboard stalls |
| memory gain | lower memory latency, fewer misses/replays/bank conflicts/MSHR stalls, higher coalescing efficiency |
| compute gain | higher FU utilization, lower execute latency, fewer issue/operand stalls |
| launch/runtime gain | lower queue wait, launch latency, transfer/fence overhead |
| config effect | topology/resource change tied to generated config and capability output |
| artifact/noise | tool variance, workload sampling, frequency change, incorrect baseline, missing correctness gate |

Do not claim cause from a single summary speedup number.

## 10. State Evolution

PPA state evolves from verified baseline and variant records into a causal evidence graph. Each metric change must be traced to a changed GPU state, then routed as feedback to the contract owner that can act on it.

## 11. Evidence Graph

Every report should build this graph:

```text
controlled diff
  -> changed GPU state
  -> changed counter/trace event
  -> changed metric
  -> supported claim
  -> feedback target
```

Example feedback targets:

- architecture: revise state contract or invariant.
- config: add derived parameter, legality check, or config ID field.
- runtime: change launch/queue/fence behavior.
- golden sim: add trace field or semantic/timing check.
- RTL: fix scheduler, pipeline, scoreboard, or counter owner.
- memory: fix coalescer/cache/MSHR/replay/fence behavior.

## 12. Output Contract

PPA output must include:

- baseline record.
- variant record.
- workload model.
- metric table.
- correctness gate status.
- counter/trace provenance.
- area/timing/power provenance where used.
- causal attribution graph.
- limitations and next feedback target.

## 13. Verification Gate

| Gate | Required proof |
|---|---|
| correctness | baseline and variant pass smoke/regression/oracle trace gate |
| reproducibility | commands, config digests, report paths, workload inputs are recorded |
| controlled diff | exactly one intended variable changed or result is labeled exploratory |
| counter audit | counters map to owner modules and explain metric direction |
| physical audit | tool/device/technology/clock/activity source are recorded |
| attribution | evidence graph connects state change to metric change |
| feedback | next architecture/config/RTL/memory/runtime action is identified |

## 14. Design Evidence Layer

Use references only as evidence:

| Evidence | Use |
|---|---|
| GPGPU-Sim/AccelWattch | behavioral and power-model evidence for simulator counters, traces, activity, model caveats |
| Rocket Chip | structural reference for local perf events, generated configs, harness/regression evidence |
| Vortex/MIAOW | implementation anchors for GPU synthesis, FPGA, benchmark, and prototype credibility evidence |
| XiangShan | tradeoff justification for HPM ownership, top-down bottleneck decomposition, checkpoint methodology |
| papers | empirical justification only when baseline, variant, workload, and limitations are comparable |

Frameworks and papers support evidence nodes; they must not be report sections that replace causal analysis.

## 15. Failure Modes

- Speedup is reported without baseline, variant, workload, config, and correctness gate.
- Multiple variables changed but claim is written as a causal conclusion.
- Simulator counters are treated as silicon timing or power.
- SAIF/VCD, power model, or synthesis report is detached from workload/config.
- Counter names exist but producer modules and trigger conditions are unknown.
- PPA feedback does not route back to a specific contract owner.
