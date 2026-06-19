# GPGPU-Sim Local Reference For GPGPU PPA Evaluation

This note expands the GPGPU-Sim references that matter for the `gpgpu-ppa-evaluation` skill. It focuses on reproducible simulator configs, runtime/cycle/memory counters, trace sampling, visualization, and AccelWattch power modeling.

Terminology note: this file preserves GPGPU-Sim source names such as `warp`, `CTA`, `shader`, `SM`, and `memory partition`. In the skill contract, map them to `SIMT group`, CTA/workgroup, compute core/CU, and memory hierarchy owner names.

## What GPGPU-Sim Teaches For This Skill

GPGPU-Sim makes performance and power evidence depend on a recorded workload/config path:

- `gpgpusim.config` defines architecture, runtime limits, timing, memory, stats, trace, and power settings;
- runtime and shader/memory models accumulate counters during the same kernel launch path;
- memory latency, cache, interconnect, DRAM, and traffic stats explain bottlenecks;
- AerialVision visualizes performance behavior;
- AccelWattch consumes activity/counter data through `power_interface` and power config.

The local lesson is that PPA reports should bind workload, config, backend, counters, trace, and power model assumptions. A speedup without stall/counter explanation is not enough.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/gpgpusim.md` | PPA lessons and caveats. |
| `ref_submodule/gpgpu-sim/configs/tested-cfgs/SM86_RTX3070/gpgpusim.config` | Reproducible config record. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/stat-tool.*` | Runtime and simulator statistics. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/stats.h` | Stats data structures and categories. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/mem_latency_stat.*` | Memory latency breakdown. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/visualizer.*` | AerialVision output hooks. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/power_config` in `gpu-sim.cc` | Power option registration. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/power_interface.*` | Activity/counter handoff to power model. |
| `ref_submodule/gpgpu-sim/src/accelwattch/` | AccelWattch model implementation. |
| `ref_submodule/gpgpu-sim/src/trace.*` | Trace component and sampling config. |

## Evidence Loop

For a local PPA report, use a GPGPU-Sim-style loop:

1. Record workload, input size, kernel name, launch shape, and runtime path.
2. Record config file or config digest.
3. Run correctness gate first.
4. Collect core counters: cycles, instructions, issued SIMT groups, scheduler stalls, scoreboard stalls, FU utilization.
5. Collect memory counters: load/store count, cache hit/miss, MSHR stalls, memory latency, DRAM queue/bank behavior, interconnect pressure.
6. Collect trace samples when counters are insufficient to explain the result.
7. If power is reported, record model version, XML/config file, activity source, and calibration caveat.
8. Compare against a baseline with one intended variable changed.

## Counter Categories To Borrow

| Category | Examples |
|---|---|
| runtime | kernel launch count, launch latency, stream/queue behavior, memcpy timing |
| core | cycles, committed instructions, issue rate, active/idle SIMT groups |
| scheduler | scoreboard block, operand block, memory block, barrier block, replay |
| memory | load/store requests, memory latency, cache misses, bank conflicts, MSHR stalls |
| hierarchy | L1/L2/ICNT/DRAM queue occupancy or stalls |
| power | per-cycle dump, metric trace, aggregate energy/power, steady-state window |
| trace | sampled components, sampled core, sampled memory partition |

## Power Caveats

AccelWattch is useful as a power-modeling reference, but local reports must say whether power is:

- measured on hardware;
- produced by synthesis/PnR with activity;
- vectorless estimate;
- simulator activity proxy;
- borrowed from a calibrated external model.

Do not present simulator power as silicon power without calibration and workload-specific activity.

## Reporting Template

Minimum report fields:

| Field | Required detail |
|---|---|
| config | file path or digest, architecture parameters, clock domains |
| workload | kernel, input, launch dimensions, memory image |
| backend | functional sim, timing sim, RTL sim, FPGA, synthesis, power model |
| correctness | pass/fail and trace/regression state |
| counters | cycles, instructions, stalls, memory hierarchy, runtime stats |
| reports | trace path, visualizer output, power output, synthesis/FPGA reports |
| interpretation | supported conclusion and explicit non-claims |

## Caveats

- GPGPU-Sim timing counters are simulator evidence, not RTL timing closure.
- AccelWattch numbers depend on model configuration and calibration target.
- A config change can invalidate PPA comparison even if the workload is unchanged.
- Trace sampling can hide rare events; use full traces for correctness bugs.

