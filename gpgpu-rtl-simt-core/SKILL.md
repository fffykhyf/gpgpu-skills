---
name: gpgpu-rtl-simt-core
description: Use when designing, editing, or reviewing GPGPU SIMT RTL such as SIMT group lifecycle, PC, active masks, IPDOM, split/join, fetch/decode, scheduler, scoreboard, operands, register file, functional units, valid-ready, stall, flush, or commit behavior.
---

# GPGPU RTL SIMT Core

## Overview

Use this skill for the minimal compute core of a GPGPU. Keep SIMT state explicit, keep module boundaries small, and keep RTL behavior comparable to the simulator trace. Use Rocket Chip as a reference for typed parameters, optional unit hooks, ready-valid interfaces, command/response arbitration, local perf events, and generated tile integration. Do not use Rocket's scalar in-order pipeline as a SIMT execution template.

## Core Rule

For every RTL change, define the state contract before editing logic:

- PC per SIMT group.
- Active lane mask and predicate behavior.
- SIMT group lifecycle: inactive, ready, issued, waiting, barrier, replay, done.
- IPDOM, split, join, branch, and reconvergence state if control flow changes.
- Register file read/writeback and write conflict rules.
- Scoreboard set, clear, flush, reset, and kill rules.
- Pipeline valid-ready, stall, flush, reset, and kill behavior.
- Optional feature ownership: decode hook, issue packet fields, ports, config bit, trace field, perf event, and test gate.
- Protocol boundary: request/response fields, source/tag lifetime, nack/replay/kill priority, and monitor point for LSU or control-plane interfaces.

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
| integration shell | expose configured ports, debug/perf/trace, runtime-visible status, and protocol monitor hooks |

Avoid a single module that schedules, decodes, reads registers, executes, writes back, and drives memory.

## GPGPU-Sim Translation Rules

Use GPGPU-Sim's shader core as a state checklist, not an RTL template:

| GPGPU-Sim anchor | RTL owner to define |
|---|---|
| `shd_warp_t` | resident SIMT-group table: valid, PC, active mask, waiting, outstanding stores, instruction buffer |
| `simt_stack` | branch/divergence/reconvergence state and active-mask update rules |
| `scheduler_unit::cycle()` | readiness equation, issue arbitration, stall reason, FU availability |
| `scoreboard` | register dependency set/clear, flush, kill, and reset behavior |
| `opndcoll_rfu_t` | operand collector, register-bank pressure, and read-port arbitration |
| `issue_warp()` | accepted issue packet with SIMT context and scoreboard reserve |
| `writeback()` | destination write, scoreboard release, pipeline count update, trace event |

Translate every C++ queue, vector, and helper call into explicit capacity, valid-ready, reset, flush, and kill behavior.

## Rocket Chip RTL Integration Pattern

Use Rocket Chip as the reference for integrating optional units without blurring ownership:

| Pattern | Rocket Chip anchor | Local SIMT rule |
|---|---|---|
| typed core params | `RocketCoreParams`, `RocketTileParams` | Keep feature flags, widths, counters, and optional ports in a typed config surface. |
| optional decode hooks | Rocket decode table with optional M/A/F/D/RoCC/vector features | New uop classes must declare decode, issue, scoreboard, writeback, trace, and test effects together. |
| ready-valid interfaces | `DecoupledIO`, `HellaCacheIO`, RoCC cmd/resp | Define backpressure, kill, nack, replay, exception, and response arbitration explicitly. |
| accelerator command path | `LazyRoCC.scala` command router and response arbiter | Treat external or optional execution units as command/response clients with busy, fault, and interrupt/status semantics. |
| local events | Rocket event sets and cache perf events | Add perf events close to scheduler, scoreboard, LSU, and FU owners. |

Borrow the integration pattern. Do not replace SIMT scheduler, active-mask, reconvergence, CTA, or lane semantics with CPU concepts.

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
- protocol-visible fields such as source/tag, byte mask, lane mask, ordering, exception, or completion status.
- perf/debug/trace counters or runtime-visible status.

An issue packet should carry at least simt_group_id, PC, active lane mask, opcode/FU type, source and destination fields, memory metadata, scheduler or issue slot ID when relevant, and trace identity.

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

For deeper GPGPU-Sim background tied to this skill, read `gpgpusim_local.md` in this directory. It explains `shd_warp_t`, `simt_stack`, scheduler readiness, dynamic `warp_inst_t` issue packets, scoreboard release, operand collection, and RTL translation caveats.

For Rocket Chip background tied to this skill, read `../../ref/skillref/rocket.md` and then inspect `../../ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala`, `tile/RocketTile.scala`, `tile/BaseTile.scala`, `tile/LazyRoCC.scala`, and `rocket/HellaCache.scala` when needed.

## Common Mistakes

- Treating active mask as a temporary signal instead of core SIMT state.
- Adding branch or barrier behavior without reconvergence or wakeup rules.
- Hiding hazard behavior inside operand read logic.
- Letting backpressure rely on implicit ordering between unrelated always blocks.
- Copying GPGPU-Sim C++ timing order without specifying RTL handshakes, table capacity, and reset/flush behavior.
- Debugging only through waveform browsing instead of simulator/RTL trace alignment.
- Copying Rocket's scalar core structure instead of only borrowing its config, optional-unit, ready-valid, event, and integration patterns.
- Adding an optional unit without decode, scoreboard, trace, perf, config, and protocol ownership.
