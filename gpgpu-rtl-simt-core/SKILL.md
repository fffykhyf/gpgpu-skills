---
name: gpgpu-rtl-simt-core
description: Use when designing, editing, or reviewing GPGPU SIMT RTL such as SIMT group lifecycle, PC, active masks, IPDOM, split/join, fetch/decode, scheduler, scoreboard, operands, register file, functional units, valid-ready, stall, flush, or commit behavior.
---

# GPGPU RTL SIMT Core

## Overview

Use this skill for the minimal compute core of a GPGPU. Keep SIMT state explicit, keep module boundaries small, and keep RTL behavior comparable to the simulator trace.

## Core Rule

For every RTL change, define the state contract before editing logic:

- PC per SIMT group.
- Active lane mask and predicate behavior.
- SIMT group lifecycle: inactive, ready, issued, waiting, barrier, replay, done.
- IPDOM, split, join, branch, and reconvergence state if control flow changes.
- Register file read/writeback and write conflict rules.
- Scoreboard set, clear, flush, reset, and kill rules.
- Pipeline valid-ready, stall, flush, reset, and kill behavior.

If these cannot be stated cleanly, the module boundary is too broad or the architecture contract is incomplete.

## Terminology Contract

Use canonical terms for local design contracts. Preserve source aliases only when naming Vortex or MIAOW signals.

| Canonical term | Source aliases | RTL contract |
|---|---|---|
| SIMT group | warp, wavefront, wave | scheduling unit with one PC and active lane mask |
| simt_group_id | warp ID, `wfid`, wave ID, wavefront tag | table index for readiness, waits, trace, and completion |
| active lane mask | active mask, thread mask, `tmask`, `EXEC` mask | lane participation state owned by scheduler/divergence/exec logic |
| CTA/workgroup | CTA, block, workgroup | barrier and launch context containing SIMT groups |
| compute core/CU | core, CU, compute unit | owner of resident SIMT groups and execution units |

## Preferred Pipeline Boundaries

| Stage or unit | Responsibility |
|---|---|
| schedule | choose a ready SIMT group, expose stall reason, track lifecycle |
| fetch | request instruction by PC and handle I-cache response |
| decode | turn instruction bits into control fields |
| issue | buffer decoded instructions, check hazards, select issue slots |
| operands | read registers without hiding hazard ownership |
| dispatcher | route issue slots to ALU/FPU/LSU/SFU/TCU |
| execute | produce unit results and memory requests |
| commit | apply writeback, update scoreboard, emit trace |

Avoid a single module that schedules, decodes, reads registers, executes, writes back, and drives memory.

Before implementing issue or hazard logic, the state contract must also list the per-SIMT-group tables that own readiness:

| Table | Owns |
|---|---|
| valid entry | decoded instruction residency and removal on halt, branch, waitcnt, barrier, or issue |
| FU class | SALU, SIMD, SIMF, LSU destination for the resident instruction |
| GPR dependency | SGPR/VGPR source and destination readiness |
| SPR dependency | EXEC, VCC, SCC, M0 readiness |
| memory wait | LSU in-flight block and release by done simt_group_id |
| branch wait | branch issued but not resolved |
| barrier wait | CTA/workgroup barrier arrival and release |
| in-flight limit | maximum outstanding instruction or finished-SIMT-group state |

Use an explicit readiness equation. A concrete LSU issue condition is:

```text
ready = fu_lsu & valid & gpr_spr_ready & ~max_inflight & ~mem_wait & ~branch_wait & ~barrier_wait
```

For non-LSU units, remove only the wait terms that truly do not apply. Do not collapse these owners into a single unexplainable `ready`.

## Instruction Impact Checklist

For each instruction or uop class, state whether it changes:

- PC or next PC.
- active lane mask, predicate mask, split/join stack, or SIMT group status.
- integer, floating, vector, or predicate registers.
- scoreboard or in-flight state.
- memory request, response, fence, or replay state.
- barrier, CTA, CSR, or launch-visible state.

## Bring-Up Order

1. Single SIMT group, single issue, ALU-only, no divergence.
2. Multi-SIMT-group round-robin scheduler.
3. Register writeback and scoreboard.
4. Active mask and predicated execution.
5. Branch plus simplified divergence/reconvergence state.
6. LSU connection through the memory-path contract.
7. Barrier, CTA/workgroup dispatch, and full SIMT group lifecycle.

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains SIMT state, scheduler/fetch/decode/issue/execute/commit boundaries, and simulator-aligned RTL contracts.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the CU RTL path, fetch and wavepool state, issue readiness equations, scoreboard dependency tables, EXEC/VCC/SCC/M0 ownership, FU writeback, and trace signals.

## Common Mistakes

- Treating active mask as a temporary signal instead of core SIMT state.
- Adding branch or barrier behavior without reconvergence or wakeup rules.
- Hiding hazard behavior inside operand read logic.
- Letting backpressure rely on implicit ordering between unrelated always blocks.
- Debugging only through waveform browsing instead of simulator/RTL trace alignment.
