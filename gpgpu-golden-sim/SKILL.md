---
name: gpgpu-golden-sim
description: Use when designing or debugging a GPGPU golden simulator, SimX-like module twin, instruction semantics, trace schema, RTL-vs-simulator comparison, execution mismatch, first divergence, or regression workflow.
---

# GPGPU Golden Simulator

## Overview

Use this skill when simulator behavior, instruction semantics, or trace comparison is the source of truth. The simulator should be an executable twin of the architecture and a practical oracle for RTL debug, not just a final-output checker.

## Core Rule

Every non-trivial RTL behavior needs either simulator behavior or a golden trace before the RTL is trusted. For bugs, find the first divergence between the reference and implementation before proposing a hardware fix. Use the smallest oracle that proves the current stage:

| Stage | Oracle | Use when |
|---|---|---|
| G0 | hand-written expected side effects | tiny ALU, branch, or LSU unit tests |
| G1 | external ISA simulator trace | expanding instruction coverage before a full local simulator exists |
| G2 | normalized per-SIMT-group trace | debugging multi-SIMT-group RTL effects |
| G3 | module-level golden model | scoreboard, LSU, branch, or barrier ownership is under test |
| G4 | cycle-aware simulator | stalls, counters, and PPA interpretation depend on timing |

External functional traces and normalized per-SIMT-group RTL traces are valid as an early correctness loop, but they are not a cycle model.

## Terminology Contract

Use canonical trace terms in schemas and mismatch reports. Keep reference names only when quoting a backend.

| Canonical term | Source aliases | Trace meaning |
|---|---|---|
| SIMT group | warp, wavefront, wave | scheduled execution stream with one PC and active lane mask |
| simt_group_id | warp ID, `wfid`, wave ID, wavefront tag | stable identity used to group trace events |
| active lane mask | active mask, thread mask, `tmask`, `EXEC` mask | lane participation state at an event |
| CTA/workgroup | CTA, block, workgroup | launch/barrier/local-memory scope |
| compute core/CU | core, CU, compute unit | trace source that owns SIMT groups |

## Module Twin Map

For every new RTL block, state whether the simulator has a matching owner:

| Hardware concept | Simulator owner to define |
|---|---|
| SIMT-group scheduler, PC, masks, barriers | scheduler or SIMT-group state model |
| decode and instruction expansion | decoder and sequencer |
| scoreboard and hazards | scoreboard model |
| register read/writeback | operand or register-file model |
| ALU/FPU/SFU/LSU/TCU | functional unit model |
| memory hierarchy | LSU, coalescer, cache, memory model |
| launch and CTA/workgroup dispatch | runtime/KMU/CTA/workgroup model |

Avoid a central interpreter that bypasses the timing/module boundary. ISA semantics should live close to the unit that owns the corresponding behavior.

## Trace Contract

A useful trace record should include:

| Category | Fields |
|---|---|
| identity | cycle or step, sequence ID or UUID, compute core/CU ID, simt_group_id |
| control | PC, next PC, opcode, active lane mask, predicate mask |
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

Do not edit the simulator merely to match RTL output. First decide which side violates the architecture contract. Trace comparison must also:

- Normalize external traces before comparison; never diff raw simulator logs with RTL logs.
- Keep per-SIMT-group streams or stable identity fields so interleaving does not hide the first divergence.
- Distinguish content differences from missing trace or hang conditions.
- Trace architectural side effects first: register writes, special register writes, memory load/store effects, branch, barrier, waitcnt, and retire PC.
- Record the external oracle version, command, input memory, instruction memory, and launch/config files.

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains the SimX executable twin and module-aligned simulator/RTL contracts.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the Multi2Sim trace flow, trace parser, tracemon data structures and print functions, trace comparator, regression runner, and what MIAOW's oracle does not prove.

## Common Mistakes

- Comparing only final memory output when the first wrong writeback happened earlier.
- Adding trace fields only after a bug appears instead of defining a minimal trace contract early.
- Mixing functional correctness and timing fidelity in one unclear trace.
- Keeping simulator structure unrelated to RTL, making trace diffs hard to map back.
- Declaring a fix without rerunning the reproducer and at least one regression.
