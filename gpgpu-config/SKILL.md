---
name: gpgpu-config
description: Use when adding, editing, or reviewing GPGPU parameters, generated config, hardware-private knobs, simulator-private knobs, HW/SW ABI constants, CSR or DCR maps, memory maps, kernel ABI values, device capabilities, backend config drift, or hard-coded core/warp/thread/cache values.
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

## Change Checklist

For every config change:

- Name the class of the parameter.
- Identify its single source of truth.
- List generated or synchronized consumers.
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

## Drift Signals

Use this skill immediately when you see:

- lane, warp, core, register, cache, or memory sizes copied in multiple files.
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

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It summarizes the relevant Vortex design documents and code paths so routine config and ABI work does not require re-reading the whole reference tree.
