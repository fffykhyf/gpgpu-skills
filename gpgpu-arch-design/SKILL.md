---
name: gpgpu-arch-design
description: Use when planning, staging, or reviewing simple GPGPU architecture design across ISA, SIMT execution, simulator, RTL, runtime, tests, performance counters, memory hierarchy, PPA, FPGA bring-up, or project roadmap decisions.
---

# GPGPU Architecture Design

## Overview

Use this skill as the top-level guardrail for local GPGPU development. It keeps work staged around a runnable, observable path instead of letting ISA, RTL, runtime, and performance work drift together.

## Core Rule

Before changing or proposing any GPGPU feature, classify the task into one or more layers:

| Layer | Typical artifacts | Required question |
|---|---|---|
| ISA | instruction semantics, encoding, assembler rules | What architectural state changes? |
| Simulator | functional model, cycle model, golden trace | What is the reference behavior? |
| RTL | pipeline, SIMT core, LSU, cache, interconnect | What is the valid-ready and stall contract? |
| Runtime | launch ABI, host/device contract, buffers | How does software start and observe work? |
| Tests | smoke tests, trace diff, regressions | What proves this stage works? |
| Evaluation | counters, logs, PPA reports | What metric justifies the change? |
| Docs | architecture notes, design decisions | What does the next agent need to know? |

Do not silently modify multiple layers. Name the affected layers and add the smallest verification path for each.

## Stage Order

Follow this order unless the user explicitly scopes a narrower investigation:

1. Define the project skeleton, ISA sketch, SIMT state, and centralized configuration.
2. Build or update the simulator/golden model before complex RTL.
3. Implement the minimal SIMT core: warp state, active mask, scheduler, register file, ALU, commit.
4. Add the memory path: blocking LSU first, lane mask and byte enable next, coalescing/cache later.
5. Define the runtime or testbench launch contract: load program, load args, start, done, read result.
6. Add counters before performance tuning: cycles, instructions, warp stalls, memory stalls, load/store counts.
7. Add memory hierarchy only after traces and counters show the bottleneck.
8. Move to synthesis, FPGA, PPA, VM, tensor, or software ecosystem work only after the basic loop is stable.

## Required Output For Design Work

When asked to design or extend the GPGPU, produce:

- Scope: affected layers and non-goals.
- State contract: PC, active mask, warp state, registers, memory, and launch state if relevant.
- Execution path: simulator behavior, RTL module boundary, and runtime/test entry.
- Verification: smallest smoke test, trace diff plan, and required counters.
- Deferral list: advanced features intentionally left out.

## Common Mistakes

- Starting RTL before a reference model exists.
- Adding cache, VM, tensor, OpenCL, or HIP before a minimal SIMT loop is debuggable.
- Treating tests as final output checks instead of traceable behavior checks.
- Hard-coding core, warp, lane, register, or memory sizes across unrelated files.
- Letting testbench-only pokes become the permanent runtime interface.
