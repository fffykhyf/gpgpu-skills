---
name: gpgpu-golden-sim
description: Use when designing or debugging a GPGPU golden simulator, SimX-like module twin, instruction semantics, trace schema, RTL-vs-simulator comparison, execution mismatch, first divergence, or regression workflow.
---

# GPGPU Golden Simulator

## Overview

Use this skill when simulator behavior, instruction semantics, or trace comparison is the source of truth. The simulator should be an executable twin of the architecture and a practical oracle for RTL debug, not just a final-output checker.

## Core Rule

Every non-trivial RTL behavior needs either simulator behavior or a golden trace before the RTL is trusted. For bugs, find the first divergence between the reference and implementation before proposing a hardware fix.

## Module Twin Map

For every new RTL block, state whether the simulator has a matching owner:

| Hardware concept | Simulator owner to define |
|---|---|
| warp scheduler, PC, masks, barriers | scheduler or warp state model |
| decode and instruction expansion | decoder and sequencer |
| scoreboard and hazards | scoreboard model |
| register read/writeback | operand or register-file model |
| ALU/FPU/SFU/LSU/TCU | functional unit model |
| memory hierarchy | LSU, coalescer, cache, memory model |
| launch and CTA dispatch | runtime/KMU/CTA model |

Avoid a central interpreter that bypasses the timing/module boundary. ISA semantics should live close to the unit that owns the corresponding behavior.

## Trace Contract

A useful trace record should include:

| Category | Fields |
|---|---|
| identity | cycle or step, sequence ID or UUID, core ID, warp ID |
| control | PC, next PC, opcode, active mask, predicate mask |
| operands | source registers, source values, destination register |
| commit | writeback valid, value, exception or illegal instruction |
| memory | op, lane mask, address, byte enable, data, tag, response |
| scheduling | scoreboard block, operand block, memory block, barrier block, replay |

If a field is omitted, say why it is not needed at this stage.

## First-Divergence Workflow

1. Define instruction semantics before implementation: inputs, outputs, state changes, illegal cases, and mask behavior.
2. Add or update simulator behavior before complex RTL.
3. Emit the smallest golden trace that exercises the behavior.
4. Run RTL or the second backend on the same program, config, input memory, and launch shape.
5. Diff ordered architectural effects first, then timing fields.
6. Report the first divergent event with enough context to reproduce it.
7. Decide whether simulator, RTL, memory path, runtime, or test harness violated the contract.

Do not edit the simulator merely to match RTL output. First decide which side violates the architecture contract.

## Common Mistakes

- Comparing only final memory output when the first wrong writeback happened earlier.
- Adding trace fields only after a bug appears instead of defining a minimal trace contract early.
- Mixing functional correctness and timing fidelity in one unclear trace.
- Keeping simulator structure unrelated to RTL, making trace diffs hard to map back.
- Declaring a fix without rerunning the reproducer and at least one regression.

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It summarizes the relevant Vortex design documents and code paths so routine simulator and trace work does not require re-reading the whole reference tree.
