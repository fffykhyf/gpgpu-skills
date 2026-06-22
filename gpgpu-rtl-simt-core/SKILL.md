---
name: gpgpu-rtl-simt-core
description: Use when designing, editing, or reviewing GPGPU SIMT RTL such as SIMT group lifecycle, PC, active masks, IPDOM, split/join, fetch/decode, scheduler, scoreboard, operands, register file, functional units, valid-ready, stall, flush, or commit behavior.
---

# GPGPU RTL SIMT Execution State Machine Skill

## 1. Objective

Implement the compute core as a warp/SIMT execution FSM whose PC, active mask, register, scoreboard, memory, and pipeline state transitions are traceable against the semantic oracle.

## 2. Input Contract

Input is an RTL execution intent with config digest, launch descriptor shape, instruction subset, oracle trace requirement, memory request contract, and target bring-up gate.

## 3. SIMT State Model

| State | Owner | Consumers |
|---|---|---|
| PC per SIMT group | fetch/divergence unit | instruction fetch, trace, branch update |
| active lane mask | divergence/predicate unit | decode, issue, FU lanes, memory coalescer, trace |
| register file | register/operand unit | operand read, writeback, oracle diff |
| scoreboard/dependency graph | issue/writeback/hazard unit | scheduler readiness, operand read, replay |
| pending memory ops | LSU/memory interface | scheduler wait, response demux, writeback |
| barrier/replay state | CTA/workgroup control and replay owner | scheduler readiness, pipeline kill/reissue |
| pipeline registers | fetch/decode/issue/execute/writeback units | valid-ready, stall, flush, trace |

Keep these owners separate enough that each state transition can be tested and traced.

## 4. Mandatory Five Questions

For every RTL change answer:

1. What state exists? Name the SIMT group, mask, register, dependency, memory, or pipeline state.
2. Who produces it? Name the RTL unit and accepted input event.
3. Who consumes it? Name scheduler, FU, LSU, writeback, runtime status, trace, or PPA counter.
4. How does it change? Define reset, issue, stall, completion, replay, flush, kill, and done transitions.
5. How do we verify it? Name oracle diff, assertion, unit test, trace check, or regression.

## 5. Transformation Rules: Pipeline FSM

The baseline pipeline state machine is:

```text
fetch -> decode -> issue -> execute -> writeback
```

| Stage | Input state | Transformation | Output state | Gate |
|---|---|---|---|---|
| fetch | ready SIMT group and PC | request instruction, handle stall/flush | instruction word and PC trace | fetch trace matches oracle PC |
| decode | instruction word/config | produce uop, operands, FU class, control metadata | decode packet | illegal/unsupported op test |
| issue | decoded packet, mask, scoreboard, FU availability | reserve dependencies and select FU | issue packet | scoreboard set/assertion |
| execute | issue packet | compute ALU/FPU/SFU/control or memory request | result, branch update, memory op | oracle semantic diff |
| writeback | result or memory response | update register file, scoreboard, PC/mask/done state | committed trace event | trace diff and dependency release |

Every valid-ready boundary must define stall, flush, kill, replay, and reset priority.

## 6. Warp Scheduler Policy

Scheduler readiness must be an explicit equation over owned state. Example:

```text
ready =
  valid
  & instruction_available
  & active_mask_nonzero
  & scoreboard_sources_ready
  & fu_available
  & ~memory_wait
  & ~barrier_wait
  & ~replay_wait
  & ~done
```

For each scheduler policy, state:

- arbitration rule: round-robin, age, priority, or fixed.
- fairness/deadlock assumption.
- stall reason priority.
- how branch, barrier, memory, and replay states block or release readiness.
- counters produced for PPA.

## 7. Hazard Rules

| Hazard | Rule |
|---|---|
| RAW | issue only when all source dependencies are clear or bypass is explicitly defined |
| WAR/WAW | define whether pipeline is in-order enough to avoid them or add dependency tracking |
| scoreboard set | reserve destination before accepted issue |
| scoreboard clear | clear only on owning writeback/kill/flush transition |
| memory dependency | pending memory op owns wait state until response/fault/replay/fence completion |
| divergence | branch updates PC/mask/reconvergence state atomically with trace event |
| replay/kill | replay must preserve or reconstruct issue packet and dependency state |
| barrier | CTA/workgroup arrival/release must not strand active SIMT groups |

## 8. Issue Packet Contract

An accepted issue packet must carry:

- kernel ID, compute core/CU ID, simt_group_id.
- PC and next-PC metadata.
- active lane mask and predicate mask.
- opcode, FU class, instruction modifiers.
- source/destination register IDs and register class.
- scoreboard reservation metadata.
- memory metadata: op, address-space class, width, lane mask, ordering/fence bits.
- trace identity and scheduler/issue-slot ID.
- kill/replay eligibility.

Missing fields must be justified by the current bring-up stage.

## 9. State Evolution

| Event | State change |
|---|---|
| launch dispatch | allocate SIMT group, initialize PC/mask/register context, clear scoreboard and pending memory |
| accepted issue | reserve destination, mark pipeline/FU busy, emit issue trace |
| ALU writeback | update register file, clear dependency, advance PC, emit commit trace |
| branch/divergence | update PC, active mask, reconvergence state, flush younger invalid work |
| memory issue | allocate pending memory entry, send memory request, block dependent readiness |
| memory response | demux by tag, update registers or fault state, clear pending memory/dependency |
| replay/nack | restore issue eligibility while preserving architectural state |
| barrier arrive/release | update CTA/workgroup barrier state and scheduler readiness |
| halt/done | mark SIMT group done and release resources deterministically |
| reset/kill | clear or restore owned state according to priority table |

## 10. Output Contract: Execution Trace Output

RTL trace must include:

- fetch/decode/issue/writeback records.
- PC, active mask, opcode, simt_group_id, scheduler decision, stall reason.
- scoreboard set/clear and dependency graph events.
- register writeback value and destination.
- memory issue/response/fault tags.
- branch/divergence and barrier events.
- config digest and launch descriptor identity.

## 11. Verification Gate

| Gate | Required proof |
|---|---|
| smoke | single SIMT group ALU-only trace matches oracle |
| scheduling | multi-SIMT group policy and stall reasons are deterministic |
| dependency | RAW and writeback scoreboard tests pass, including negative hazard case |
| mask/divergence | predicated and branch traces match oracle PC/mask transitions |
| memory interface | issue packet and memory request trace match memory-path contract |
| reset/flush/kill | priority table is asserted and covered |
| trace diff | first divergence tool can map RTL event to oracle event |

## 12. Design Evidence Layer

Use references only as evidence:

| Evidence | Use |
|---|---|
| GPGPU-Sim | behavioral evidence for warp state, SIMT stack, scheduler, scoreboard, issue/writeback traces |
| Rocket Chip | structural reference for typed params, optional hooks, ready-valid interfaces, events, integration shells |
| Vortex/MIAOW | implementation anchors for GPU SIMT pipeline boundaries, issue equations, trace signals |
| XiangShan | tradeoff justification for state ownership, derived issue/writeback ports, recovery, counter placement |
| golden sim | semantic evidence for PC/mask/register/memory side effects |

Do not copy CPU rename, ROB, scalar commit, or framework chapter structure into SIMT design.

## 13. Failure Modes

- Active mask is treated as temporary datapath instead of architectural SIMT state.
- Scheduler readiness collapses all dependency causes into one opaque `ready`.
- Scoreboard clears on the wrong response or survives kill/reset incorrectly.
- Branch updates PC without atomic mask/reconvergence state.
- Memory tags do not preserve SIMT group, lane mask, and destination.
- Waveform-only debug replaces oracle trace diff.
