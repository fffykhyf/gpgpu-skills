---
name: gpgpu-config
description: Use when adding, editing, or reviewing GPGPU parameters, generated config, hardware-private knobs, simulator-private knobs, HW/SW ABI constants, CSR or DCR maps, memory maps, kernel ABI values, device capabilities, backend config drift, or hard-coded core/SIMT-group/thread/cache values.
---

# GPGPU Config

## Overview

Use this skill when a value might drift across RTL, simulator, runtime, kernel, tests, or PPA scripts. Configuration work is not just replacing numbers with macros; it is deciding which values are private implementation knobs and which values are visible contracts.

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

## Change Checklist

For every config change:

- Name the class of the parameter.
- Identify its single source of truth.
- List generated or synchronized consumers.
- Audit duplicate appearances across Verilog `define`, Verilog parameter, C `#define`, scripts, unit-test config, FPGA scripts, generated headers, and docs.
- State whether public capability, version, or query output changes.
- Remove duplicate hard-coded copies.
- Test at least one small config and one target config.
- Update PPA config IDs if the value affects evaluation.

## Boundary Rules

- Hardware-private knobs can tune implementation but must not leak into public runtime headers.
- ABI constants must be visible to all consumers through generated headers, documented maps, or explicit capability queries.
- Debug/test knobs must not become permanent architecture assumptions.
- Derived values should be generated from source values rather than copied by hand.
- Changing a visible config without updating tests and capability reporting is a bug.
- If a MMIO map exists, list the RTL decode path, host C/C++ constants, tests, and documentation consumer before changing any offset.
- If a unit-test config format changes, update parser validation, generators, fixtures, and trace/regression expectations together.
- If a conditional build flag changes an interface, document whether it is public, FPGA-only, debug-only, or test-only.

## Drift Signals

Use this skill immediately when you see:

- lane, SIMT-group, core/CU, register, cache, or memory sizes copied in multiple files.
- simulator and RTL using different constants.
- runtime guessing hardware capability from build flags.
- tests passing only under one hard-coded configuration.
- PPA results whose config cannot be reconstructed.

## Common Mistakes

- Treating every number as the same kind of macro.
- Mixing microarchitecture knobs with software ABI constants.
- Updating RTL but leaving simulator, runtime, or tests with stale values.
- Changing memory maps or CSR/DCR numbers without a capability or version story.
- Running only the default config after changing parameterized logic.

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains generated config/type sources, ABI-visible values, DCR/capability contracts, and backend config synchronization.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the scattered constants in global definitions, dispatcher parameters, FPGA MMIO registers, Xilinx SDK offsets, unit-test config files, and SIAGen workload parameters.
