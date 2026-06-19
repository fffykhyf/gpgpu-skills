# GPGPU-Sim Local Reference For GPGPU Config

This note expands the GPGPU-Sim references that matter for the `gpgpu-config` skill. It focuses on option registration, tested config files, ownership of runtime/core/memory/power/trace knobs, and the caveats around compact string configuration.

Terminology note: this file preserves GPGPU-Sim source names such as `warp`, `CTA`, `shader`, `SM`, and `memory partition`. In the skill contract, map them to `SIMT group`, `CTA/workgroup`, `compute core/CU`, and memory hierarchy owner names.

## What GPGPU-Sim Teaches For This Skill

GPGPU-Sim treats configuration as the executable architecture instance. A single config controls functional simulation mode, runtime limits, compute capability, shader core organization, caches, shared memory, L2, interconnect, DRAM timing, stats, trace, and power modeling.

The useful pattern is ownership-based grouping:

- `power_config::reg_options()` owns AccelWattch and power activity options;
- `memory_config::reg_options()` owns DRAM, L2, memory partition, queues, and address mapping;
- `shader_core_config::reg_options()` owns shader core pipeline, caches, register files, operand collectors, schedulers, and FU counts;
- `gpgpu_sim_config::reg_options()` owns simulator limits, compute capability, runtime stack/heap/sync limits, trace options, and launch latencies.

Copy the grouping and audit discipline. Avoid copying opaque colon-separated mega-strings without parser validation and readable dumps.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/gpgpusim.md` | Config lessons and seven-skill mapping. |
| `ref_submodule/gpgpu-sim/src/option_parser.*` | Option registration/parsing framework. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc` | `reg_options()` functions for power, memory, shader core, and simulator config. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/gpu-sim.h` | Config classes and memory/shader/GPU top-level parameters. |
| `ref_submodule/gpgpu-sim/configs/tested-cfgs/SM86_RTX3070/gpgpusim.config` | Full GPU-like config instance. |
| `ref_submodule/gpgpu-sim/src/trace.*` | Trace enablement and component sampling config. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/power_*` | Power config and activity-to-power interface. |

## Config Families In GPGPU-Sim

Use these families as a local checklist:

| Family | Example GPGPU-Sim options | Skill classification prompt |
|---|---|---|
| functional simulator | `-gpgpu_ptx_sim_mode`, `-gpgpu_ptx_force_max_capability` | Is this simulator-private or architecture-visible? |
| runtime limits | stack size, heap size, pending launch count, launch latency | Is this HW/SW ABI, runtime-private, or simulator-only? |
| topology | clusters, cores per cluster, memory partitions, sub-partitions | Does this affect capability reporting and workload shape? |
| core pipeline | shader registers, CTA limit, pipeline widths, FU counts | Which RTL/simulator modules consume it? |
| scheduler | number of schedulers, issue per warp, dual issue policy | Does it change timing only or visible behavior? |
| memory | L1/L2/shared config, coalescing arch, DRAM queues, address mapping | Are request tags, cache state, and memory maps still consistent? |
| trace/stat | runtime stat period, memory latency stat, trace components | Is this debug-only or part of experiment reproducibility? |
| power | AccelWattch XML, power mode, per-cycle dump, DVFS | Is power calibrated or only an activity proxy? |

## Tested Config Discipline

`SM86_RTX3070/gpgpusim.config` is useful because it records a complete architecture instance, not just a few changed numbers. A local tested config should similarly preserve:

- target name or config ID;
- compute capability or local ISA/profile equivalent;
- topology and clock domains;
- core pipeline widths, FU counts, and latencies;
- SIMT scheduler policy;
- register/shared/cache/L2/DRAM/interconnect parameters;
- runtime launch limits;
- trace/stat/power settings;
- comments explaining compact encoded fields.

For local work, record either the config file path or a digest in every PPA or regression report.

## Compact String Caveat

GPGPU-Sim uses compact strings such as cache and DRAM timing descriptors. They are flexible, but they are hard to review. If a local project uses the same style:

- provide a parser with validation errors;
- generate a readable expanded dump;
- test at least one invalid string;
- document each field's owner and unit;
- avoid making such strings part of a public ABI unless stable.

## Local Config Rules

- Every parameter must state owner, scope, default, legal values, consumers, and test impact.
- Runtime-visible limits such as max threads, CTA size, memory map, launch latency, and pending launch count need capability reporting or documented ABI.
- Timing-only simulator knobs must not silently change RTL-visible behavior.
- Trace, stat, and power knobs belong in experiment records, not only in scripts.
- Config changes affecting memory hierarchy must update memory-path tests and PPA config IDs.

