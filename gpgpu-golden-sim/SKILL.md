---
name: gpgpu-golden-sim
description: Use when designing or debugging a GPGPU golden simulator, golden model, instruction semantics, trace format, RTL-vs-simulator comparison, execution mismatch, first divergence, or regression workflow.
---

# GPGPU Golden Simulator

## Overview

Use this skill when simulator behavior, instruction semantics, or trace comparison is the source of truth for GPGPU development. The simulator should make RTL bugs localizable, not merely predict final outputs.

## Core Rule

Every non-trivial RTL behavior needs a simulator or golden trace reference before the RTL is trusted. For bugs, locate the first behavioral divergence before proposing a hardware fix.

## Trace Contract

A useful trace record should include the fields needed to compare behavior across backends:

| Field | Purpose |
|---|---|
| cycle or step | Order events and identify first divergence |
| core, warp, lane mask | Identify the executing SIMT context |
| PC and instruction | Tie behavior to ISA semantics |
| active mask or predicate | Explain SIMT participation |
| source operands | Explain execution inputs when practical |
| register writeback | Compare architectural effects |
| memory request | Compare address, byte enable, tag, and data |
| stall or replay reason | Explain timing-visible behavior |

If a field is omitted, state why it is not needed for the current stage.

## Workflow

1. Define instruction semantics before implementation: inputs, outputs, state changes, illegal cases, and mask behavior.
2. Add or update the simulator behavior first for new ISA or execution behavior.
3. Emit a small golden trace for the smallest program that exercises the behavior.
4. Run the RTL or second backend on the same program.
5. Compare traces by ordered architectural effects first, then timing fields.
6. Report the first divergence with enough context to reproduce it.

## Debugging Discipline

For a mismatch, record:

- Reproducer: program, config, input memory, and command.
- Expected event: simulator trace line or golden state.
- Actual event: RTL trace line or observed state.
- First divergence: not the final failing output.
- Suspected layer: ISA, simulator, RTL, memory path, runtime, or test harness.
- Next verification: the smallest trace or test that will prove the fix.

## Common Mistakes

- Comparing only final memory output when the first wrong writeback happened much earlier.
- Mixing functional correctness and timing fidelity in one unclear trace.
- Treating the simulator as separate from RTL structure, making diff results hard to map back.
- Adding trace fields after a bug appears instead of defining a minimal trace contract early.
- Declaring an RTL bug fixed without rerunning the reproducer and at least one regression.
