---
name: gpgpu-config
description: Use when adding, editing, or reviewing GPGPU parameters, generated config, hardware-private knobs, simulator-private knobs, HW/SW ABI constants, CSR or DCR maps, memory maps, kernel ABI values, device capabilities, backend config drift, or hard-coded core/SIMT-group/thread/cache values.
---

# GPGPU Config

## Overview

Use this skill when a value might drift across RTL, simulator, runtime, kernel, tests, or PPA scripts. Configuration work is not just replacing numbers with macros; it is deciding which values are private implementation knobs, which values are generated from typed parameters, which values are negotiated by protocols, and which values are visible contracts. Use Rocket Chip as the model for named config fragments, derived parameters, `require`-style legality checks, and resource/capability generation. Use XiangShan as the model for large typed parameter surfaces, derived backend/cache/memory widths, config-time checks, and printed/auditable generated microarchitecture.

## Core Rule

Classify every parameter before changing it:

| Class | Meaning | Typical examples |
|---|---|---|
| hardware-private | RTL and synthesis microarchitecture only | queue depth, cache MSHR size, pipeline latency |
| simulator-private | model-only debug or timing knob | simulator verbosity, synthetic latency |
| HW/SW ABI | visible to RTL and software | CSR/DCR map, memory map, kernel args, capability bits |
| test-only | confined to tests or fixtures | small smoke-test memory size |
| debug-only | instrumentation, trace, assertions | trace level, watchdog timeout |

HW/SW ABI values need a single source of truth and a verification path through RTL, simulator, runtime, kernel, and tests.

Generator-visible values need the same discipline. If a value controls topology, address range, source/tag width, cache shape, queue depth, optional feature ports, MMIO layout, or runtime capability, define its owner, derive dependent values in one place, and reject illegal combinations before RTL or simulator execution.

## Terminology Contract

Use canonical terms in config names unless quoting source constants.

| Canonical term | Source aliases | Configuration boundary |
|---|---|---|
| SIMT group | warp, wavefront, wave | execution group width, scheduler residency, and trace identity |
| simt_group_id | warp ID, `wfid`, wave ID, wavefront tag | ID width, tag fields, trace fields, and done signals |
| active lane mask | active mask, thread mask, `tmask`, `EXEC` mask | mask width and lane-enable ABI |
| CTA/workgroup | CTA, block, workgroup | launch dimensions, group IDs, barriers, and local memory |
| compute core/CU | core, CU, compute unit | hardware capacity and resource allocation |

Do not encode source aliases into a public ABI unless the implementation already exposes that name.

For common GPGPU value families, start with this classification:

| Value family | Required classification |
|---|---|
| SIMT-group and mask sizes | SIMT-group width, active-mask width, physical SIMD width, test thread count, or FPGA prototype limit |
| SGPR/VGPR/LDS/GDS counts | physical resource, dispatch allocation unit, or test fixture value |
| dispatcher fields | HW/SW ABI, resource-private, or debug-only |
| MMIO/control offsets | HW/SW ABI requiring synchronized RTL decode, host header, tests, and docs |
| unit-test config format | test ABI with parser validation |
| conditional build flags | interface-changing, implementation-only, debug-only, or FPGA-only |

## GPGPU-Sim Config Pattern

Use GPGPU-Sim as the reference for ownership-based config grouping:

| Group | GPGPU-Sim anchor | Local rule |
|---|---|---|
| functional/runtime | `-gpgpu_ptx_sim_mode`, stack/heap/sync/pending-launch limits, launch latency | Decide whether the value is simulator-private, runtime ABI, or device capability. |
| shader core | `shader_core_config::reg_options()` | Keep topology, registers, scheduler, issue width, FU counts, and latencies tied to simulator/RTL consumers. |
| memory | `memory_config::reg_options()` | Keep cache, shared memory, L2, memory partitions, address mapping, DRAM timing, and queues in one auditable family. |
| trace/stat | `Trace`, `-gpgpu_runtime_stat`, `-gpgpu_memlatency_stat` | Treat observability knobs as part of experiment reproducibility. |
| power | `power_config::reg_options()`, AccelWattch XML/mode options | Record power model version, config file, and calibration status before making energy claims. |

If a config uses compact encoded strings like GPGPU-Sim cache or DRAM descriptors, provide parser validation and a readable expanded dump.

## Rocket Chip Config Pattern

Use Rocket Chip as the reference for generator-owned configuration:

| Pattern | Rocket Chip anchor | Local rule |
|---|---|---|
| named fragments | `Configs.scala`, `WithNBigCores`, `WithNMemoryChannels`, `WithRoccExample` | Prefer small composable config fragments over copied whole configs. |
| typed parameters | `RocketCoreParams`, `RocketTileParams`, `DCacheParams`, `L1CacheParams` | Keep related values in typed structs or schemas instead of loose constants. |
| derived values | cache/tag/row/beat/xLen-derived fields | Derive widths, masks, source IDs, and queue indexes from source values in one place. |
| legality checks | `require` in cache and tile parameter code | Fail early on illegal SIMT-group width, cacheline, bank, MSHR, queue, memory-map, or ABI combinations. |
| negotiated protocols | Diplomacy nodes, `TransferSizes`, `AddressSet`, `IdRange` | Treat bus widths, address ranges, transfer sizes, and IDs as protocol contracts, not incidental constants. |
| generated resources | DTS/resource binding, boot/debug/periphery config | Update capability/version/resource output when a public hardware feature changes. |

## XiangShan Derived-Parameter Pattern

Use XiangShan as the reference for keeping a wide configuration surface auditable:

| Pattern | XiangShan anchor | Local rule |
|---|---|---|
| named configs | `top/Configs.scala`, `BaseConfig`, `MinimalConfig` | Keep target, minimal, and experiment configs named and reproducible. |
| typed core params | `XSCoreParameters` in `Parameters.scala` | Group ISA feature flags, widths, queue sizes, memory settings, and optional units in one typed surface. |
| derived backend ports | `BackendParams.scala` | Derive issue, wakeup, read/write port, writeback, and dispatch counts from execution-unit configs. |
| cache/MMU params | `DCacheParameters`, TLB/L2TLB params | Derive tag/index/source widths, ECC bits, MSHR IDs, and cache-control ranges from source values. |
| legality checks | `require`, `configChecks` | Fail before generation when queue, bank, port, power-of-two, or ID-range combinations are illegal. |
| auditable output | backend config prints, perf parameter wiring | Dump generated topology and derived counts when they affect experiments or debug. |

For local GPGPU work, add a derived-value owner before adding a new public knob. If a parameter affects active lane mask width, source/tag width, queue capacity, register file ports, cache shape, runtime capabilities, or PPA labels, it needs a legality check and an expanded dump.

## Change Checklist

For every config change:

- Name the class of the parameter.
- Identify its single source of truth.
- List generated or synchronized consumers.
- Audit duplicate appearances across Verilog `define`, Verilog parameter, C `#define`, scripts, unit-test config, FPGA scripts, generated headers, and docs.
- State whether public capability, version, or query output changes.
- Remove duplicate hard-coded copies.
- Centralize derived values such as active-mask width, source/tag width, cacheline/beat masks, queue index bits, and memory-map ranges.
- Add legality checks for min/max values and unsupported combinations before generation.
- If a protocol width, address range, or source ID range changes, update the matching monitor, trace schema, and runtime capability.
- Record the config file path or digest when the value affects simulator, runtime, memory hierarchy, trace, or PPA reports.
- Provide a readable expanded view for compact string parameters.
- Test at least one small config and one target config.
- Update PPA config IDs if the value affects evaluation.

## Boundary Rules

- Hardware-private knobs can tune implementation but must not leak into public runtime headers.
- ABI constants must be visible to all consumers through generated headers, documented maps, or explicit capability queries.
- Debug/test knobs must not become permanent architecture assumptions.
- Derived values should be generated from source values rather than copied by hand.
- Changing a visible config without updating tests and capability reporting is a bug.
- Simulator timing knobs must not silently become RTL or runtime-visible contracts.
- Negotiated or generated protocol fields must not be duplicated as hand-written constants in RTL, simulator, or runtime code.
- If a MMIO map exists, list the RTL decode path, host C/C++ constants, tests, and documentation consumer before changing any offset.
- If a unit-test config format changes, update parser validation, generators, fixtures, and trace/regression expectations together.
- If a conditional build flag changes an interface, document whether it is public, FPGA-only, debug-only, or test-only.

## Drift Signals

Use this skill immediately when you see:

- lane, SIMT-group, core/CU, register, cache, or memory sizes copied in multiple files.
- simulator and RTL using different constants.
- runtime guessing hardware capability from build flags.
- generated parameters copied into local constants after elaboration or code generation.
- bus widths, source IDs, address sets, cacheline sizes, or queue depths that differ between producer, consumer, and monitor.
- tests passing only under one hard-coded configuration.
- PPA results whose config cannot be reconstructed.
- trace, power, or simulator results without the config file or option dump that produced them.

## Common Mistakes

- Treating every number as the same kind of macro.
- Mixing microarchitecture knobs with software ABI constants.
- Updating RTL but leaving simulator, runtime, or tests with stale values.
- Changing memory maps or CSR/DCR numbers without a capability or version story.
- Running only the default config after changing parameterized logic.
- Treating generated/negotiated values as comments instead of executable constraints.
- Adding a config fragment without naming the tests and reports that prove it works.

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains generated config/type sources, ABI-visible values, DCR/capability contracts, and backend config synchronization.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the scattered constants in global definitions, dispatcher parameters, FPGA MMIO registers, Xilinx SDK offsets, unit-test config files, and SIAGen workload parameters.

For deeper GPGPU-Sim background tied to this skill, read `gpgpusim_local.md` in this directory. It explains option registration, tested config files, runtime/core/memory/power/trace knobs, and compact string caveats.

For deeper Rocket Chip background tied to this skill, read `rocket_local.md` in this directory. It explains Config fragments, typed params, Diplomacy negotiation, RocketTile/Core/DCache params, derived fields, legality checks, and resource/capability drift lessons.

For XiangShan background tied to this skill, read `xiangshan_local.md` in this directory. It explains `Configs.scala`, `XSCoreParameters`, `BackendParams`, DCache/MMU/L2 parameters, legality checks, and the configuration drift lessons relevant to GPGPU config work.
