# Vortex Local Reference For GPGPU PPA Evaluation

This note expands the Vortex references that matter for the
`gpgpu-ppa-evaluation` skill. It focuses on reproducible performance, power,
area, timing, counters, workload/config control, SAIF/VCD activity, and report
interpretation.

## What Vortex Teaches For This Skill

Vortex ties every PPA claim to a workload, backend, configuration, correctness
state, counters, trace/activity file, and report path. A result is not just
"faster" or "smaller"; it has a command, build flags, test input, backend,
counter class, synthesis target, and interpretation boundary.

For this project, transfer these habits:

- define baseline and variant with one intended variable changed;
- record the exact config, backend, workload, and input size;
- gate performance interpretation on correctness;
- use stall/counter breakdowns before explaining speedup;
- distinguish simulator counters, RTL simulation activity, vectorless power,
  SAIF/VCD-annotated power, and post-implementation reports.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/vortex.md` | Local extraction of PPA discipline from Vortex. |
| `ref_submodule/vortex/docs/simulation.md` | Backend/app/config/perf/debug examples and common runtime execution flow. |
| `ref_submodule/vortex/docs/testing.md` | Regression and OpenCL/HIP-style test entry points for simx and rtlsim. |
| `ref_submodule/vortex/docs/debugging.md` | `--debug`, `--perf`, trace logs, trace CSV, and `--saif` capture workflow. |
| `ref_submodule/vortex/docs/synthesis_analysis.md` | Synthesis, timing, area, power, SAIF/VCD, Fmax, utilization, and report locations. |
| `ref_submodule/vortex/VX_types.toml` | MPM counters for core, stalls, memory, cache, TLB/PTW, TCU, graphics, and DXA. |
| `ref_submodule/vortex/VX_config.toml` | Hardware config variables that must be captured in any PPA record. |

## Unified Experiment Runner

`ref_submodule/vortex/ci/blackbox.sh` is the practical PPA command wrapper.

It accepts:

- backend: `--driver=gpu|simx|rtlsim|opae|xrt`;
- workload: `--app=<test/app path>`;
- architecture config: `--clusters`, `--cores`, `--warps`, `--threads`,
  `--l2cache`, `--l3cache`;
- instrumentation: `--debug`, `--scope`, `--saif`, `--perf`;
- trace outputs: `--vcd_file`, `--saif_file`, `--log`;
- app arguments: `--args`;
- isolated temp build: `--nohup`.

Internally it:

- converts CLI options to `CONFIGS` `-D` flags;
- picks the runtime backend path;
- finds the application directory under `tests/regression`, `graphics`, `mpi`,
  `opencl`, `hip`, or a direct path;
- builds the runtime driver with debug/scope/SAIF/config options;
- exports `VORTEX_PROFILING`, `VCD_FILE`, and `SAIF_FILE`;
- runs `make -C <app> run-<driver>`;
- stages a per-invocation copy of the app for `--nohup` to reduce build races.

For local PPA, this is a model for a single reproducible runner. Avoid
one-off shell snippets that lose the backend/config/workload record.

## Config Axes To Record

`ref_submodule/vortex/VX_config.toml` contains the main hardware knobs. A PPA
record should capture the ones that are relevant to the design under test:

- topology: clusters, cores, socket size;
- pipeline: warps, threads, issue width, SIMD width, operand collectors,
  barrier count;
- ISA/features: M/F/D/C/A/V, TCU, DMA/DXA, graphics/texture/raster/OM;
- memory: memory block size, address width, platform banks/data size, peak BW,
  clock rate;
- LSU: LSU lanes, blocks, line size, input/output queue size;
- cache hierarchy: enable bits, size, ways, writeback, replacement policy,
  MSHR/request/response queue sizes, bank count, memory ports;
- local memory: log size and bank count;
- VM: TLB size and pinned-region size;
- FPU/TCU implementation type and latency knobs.

`ref_submodule/vortex/docs/synthesis_analysis.md` also documents common
`CONFIGS` examples and the `NUM_CORES` shorthand. In results, prefer explicit
expanded flags over shorthand so a future reader can reconstruct the design.

## Performance Counters

`ref_submodule/vortex/VX_types.toml` defines the MPM counter naming scheme.
Useful counter groups:

- base: cycles and committed instructions;
- scheduler: scheduler idle cycles, active warps, stalled warps, issued warps,
  issued threads;
- pipeline stalls: fetch, I-buffer, scoreboard, operands, ALU, FPU, LSU, SFU,
  TCU stalls;
- control flow: branches and divergence;
- instruction mix: ALU, FPU, LSU, SFU, TCU instruction counts;
- memory from core: instruction fetches and latency, loads and latency, stores;
- caches: reads, writes, read/write misses, dirty evictions, bank stalls,
  MSHR stalls for dcache/l2/l3;
- memory class: off-chip reads/writes, memory latency, bank stalls, local memory
  reads/writes/bank stalls, coalescer misses;
- VM/MMU: TLB reads, hits, misses, evictions, PTW walks, PTW latency;
- extension units: TCU, texture, raster, OM, DXA counters when enabled.

The local interpretation rule: an IPC or runtime change is a symptom. Explain it
with issue, stall, memory, cache, and instruction mix counters before claiming
an architecture win.

## RTL Counter Sources

`ref_submodule/vortex/hw/rtl/core/VX_core.sv` is a source for core-level
performance event generation. It wires events such as instruction fetches,
loads, stores, pending read latency, scheduler activity, stalls, and FU-level
activity into MPM counters.

For local RTL PPA, counters should be generated at the event owner:

- scoreboard stalls near scoreboard;
- operand bank conflicts near operands/register file;
- LSU queue/cache stalls near memory;
- scheduler idle/active/issued near scheduler;
- FU backpressure near dispatch/FU queues.

Do not add a top-level counter that guesses why a lower-level unit stalled if
the unit can report the reason directly.

## SAIF And VCD Activity

`ref_submodule/vortex/docs/debugging.md` and
`ref_submodule/vortex/docs/synthesis_analysis.md` describe SAIF capture:

- RTL drivers such as `rtlsim`, `opaesim`, and `xrtsim` can be built with
  `SAIF=1`.
- `blackbox.sh --driver=rtlsim --app=<app> --saif` builds the simulator with
  SAIF support and runs the workload.
- `simx` does not support SAIF in `blackbox.sh`; power activity must come from
  RTL-capable backends.
- `VCD_FILE` and `SAIF_FILE` environment variables name activity outputs.
- `SAIF_INST` tells synthesis tools which simulation hierarchy prefix to strip
  so SAIF signal paths match the synthesized netlist.

`ref_submodule/vortex/hw/scripts/saif_filter.py` is useful when a master SAIF
must be sliced to a DUT subcomponent. It can list instance hierarchy, extract a
suffix-matched instance path, optionally wrap it under a chosen synthesis top,
and preserve nested scopes and net names.

Activity files are workload artifacts. Do not reuse SAIF/VCD from a different
configuration, driver, input size, or design revision.

## Power Analysis Script

`ref_submodule/vortex/hw/scripts/xilinx_power_analysis.tcl` is the Xilinx power
reference.

It:

- resolves the post-implementation checkpoint from `DCP_FILE`, `BUILD_DIR`, or
  fallback `post_impl.dcp`;
- requires `SAIF_FILE`;
- optionally uses `SAIF_INST`, or auto-detects the SAIF path prefix from the
  SAIF hierarchy and current Vivado top;
- writes a vectorless baseline report with default switching activity;
- reads SAIF and writes `read_saif_mismatch.rpt`;
- writes `power_saif.rpt`;
- deasserts resets before reporting steady-state power.

For local power work, always report whether the power number is vectorless or
activity-annotated. If SAIF annotation has many mismatches, the power result is
not strong evidence.

## Synthesis And Report Locations

`ref_submodule/vortex/docs/synthesis_analysis.md` documents several backends:
Xilinx/Vivado, Altera/Quartus, Yosys, and Synopsys Design Compiler. It also
documents DUT flows for subcomponents such as core, cache, memory unit, FPU,
TCU, lmem, and full Vortex.

Reports to preserve:

- utilization: LUT/FF/BRAM/DSP or ASIC area cells;
- timing: target period, WNS, critical path, estimated Fmax;
- methodology/DRC;
- clock and RAM utilization where available;
- vectorless power;
- VCD/SAIF-annotated power;
- mismatch report for SAIF annotation.

For Fmax, Vortex's docs use WNS to derive an estimate:
`Fmax = 1 / (clock_period - WNS)`. Record both WNS and the target period; do not
only write "timing passed".

## Minimum Local Result Record

Every local PPA result should include:

- commit or revision;
- baseline command/report path;
- variant command/report path;
- full `CONFIGS` or generated config id;
- backend and tool versions;
- workload, input size, launch shape, and app arguments;
- correctness status and known limitations;
- cycles, instructions, IPC, issue utilization;
- stall breakdown;
- load/store/cache/memory counters;
- area/utilization report paths;
- target clock, WNS, estimated Fmax;
- power mode and report path;
- interpretation: what the data supports and what it does not support.

## What Not To Copy

- Do not use Vortex benchmark choices as universal evidence.
- Do not compare different configs or workloads and call it an architecture win.
- Do not treat simulator IPC as silicon frequency or power.
- Do not report only summary numbers without commands and report paths.
- Do not interpret PPA for an incorrect design.
