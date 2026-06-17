---
name: gpgpu-rtl-simt-core
description: Use when designing, editing, or reviewing GPGPU SIMT RTL such as warp lifecycle, PC, active masks, IPDOM, split/join, fetch/decode, scheduler, scoreboard, operands, register file, functional units, valid-ready, stall, flush, or commit behavior.
---

# GPGPU RTL SIMT Core

## Overview

Use this skill for the minimal compute core of a GPGPU. Keep SIMT state explicit, keep module boundaries small, and keep RTL behavior comparable to the simulator trace.

## Core Rule

For every RTL change, define the state contract before editing logic:

- PC per warp.
- Active mask and predicate behavior.
- Warp lifecycle: inactive, ready, issued, waiting, barrier, replay, done.
- IPDOM, split, join, branch, and reconvergence state if control flow changes.
- Register file read/writeback and write conflict rules.
- Scoreboard set, clear, flush, reset, and kill rules.
- Pipeline valid-ready, stall, flush, reset, and kill behavior.

If these cannot be stated cleanly, the module boundary is too broad or the architecture contract is incomplete.

## Preferred Pipeline Boundaries

| Stage or unit | Responsibility |
|---|---|
| schedule | choose a ready warp, expose stall reason, track lifecycle |
| fetch | request instruction by PC and handle I-cache response |
| decode | turn instruction bits into control fields |
| issue | buffer decoded instructions, check hazards, select issue slots |
| operands | read registers without hiding hazard ownership |
| dispatcher | route issue slots to ALU/FPU/LSU/SFU/TCU |
| execute | produce unit results and memory requests |
| commit | apply writeback, update scoreboard, emit trace |

Avoid a single module that schedules, decodes, reads registers, executes, writes back, and drives memory.

## Instruction Impact Checklist

For each instruction or uop class, state whether it changes:

- PC or next PC.
- active mask, predicate mask, split/join stack, or warp status.
- integer, floating, vector, or predicate registers.
- scoreboard or in-flight state.
- memory request, response, fence, or replay state.
- barrier, CTA, CSR, or launch-visible state.

## Bring-Up Order

1. Single warp, single issue, ALU-only, no divergence.
2. Multi-warp round-robin scheduler.
3. Register writeback and scoreboard.
4. Active mask and predicated execution.
5. Branch plus simplified divergence/reconvergence state.
6. LSU connection through the memory-path contract.
7. Barrier, CTA dispatch, and full warp lifecycle.

## Common Mistakes

- Treating active mask as a temporary signal instead of core SIMT state.
- Adding branch or barrier behavior without reconvergence or wakeup rules.
- Hiding hazard behavior inside operand read logic.
- Letting backpressure rely on implicit ordering between unrelated always blocks.
- Debugging only through waveform browsing instead of simulator/RTL trace alignment.

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It summarizes the relevant Vortex design documents and code paths so routine SIMT RTL work does not require re-reading the whole reference tree.
