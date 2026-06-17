---
name: gpgpu-rtl-simt-core
description: Use when designing, editing, or reviewing GPGPU SIMT RTL such as warp state, active masks, fetch/decode, scheduler, scoreboard, operand collection, register file, ALU, functional units, pipeline control, valid-ready, stall, flush, or commit behavior.
---

# GPGPU RTL SIMT Core

## Overview

Use this skill for the minimal compute core of a GPGPU. Keep SIMT architectural state explicit and keep RTL module boundaries small enough to test and trace.

## Core Rule

For every RTL change, define the state contract before editing logic:

- PC per warp.
- Active mask and predicate behavior.
- Warp status: idle, ready, running, stalled, done, waiting at barrier, or replaying.
- Register file read and writeback rules.
- Scoreboard or hazard rules.
- Pipeline valid-ready, stall, flush, reset, and kill behavior.

If these cannot be stated cleanly, the module boundary is probably too broad.

## Preferred Module Boundaries

| Module area | Responsibility |
|---|---|
| Warp scheduler | Select a ready warp and expose stall reasons |
| Fetch/decode | Translate PC and instruction bits into control fields |
| Scoreboard | Track register and memory hazards |
| Operand collector | Gather source operands without hiding hazards |
| Register file | Own architectural register storage and writeback conflict rules |
| Functional units | Execute ALU, branch, SFU, or other operations |
| Commit/writeback | Apply architectural effects and emit trace events |

Avoid a single module that decodes, schedules, reads registers, executes, writes back, and controls memory.

## Implementation Checklist

Before changing RTL:

- Identify the corresponding simulator behavior or golden trace.
- State whether the change is architectural, timing-only, or test-only.
- Define affected signals and their valid cycles.
- State backpressure behavior for each interface.
- Add or update a smoke test that reaches the changed path.

After changing RTL:

- Compare simulator and RTL architectural effects.
- Check reset behavior and empty/invalid input behavior.
- Check at least one stall or backpressure case if the interface can stall.
- Preserve trace visibility for PC, warp, active mask, writeback, and memory events.

## Common Mistakes

- Treating active mask as a temporary implementation detail instead of core SIMT state.
- Adding branch or barrier behavior without specifying reconvergence or wakeup rules.
- Hiding hazard behavior inside operand read logic.
- Making stall handling depend on implicit ordering between unrelated always blocks.
- Debugging RTL only through waveform browsing instead of trace alignment.
