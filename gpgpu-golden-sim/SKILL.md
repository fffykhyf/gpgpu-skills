---
name: gpgpu-golden-sim
description: Use when designing or debugging a GPGPU golden simulator, SimX-like module twin, instruction semantics, trace schema, RTL-vs-simulator comparison, execution mismatch, first divergence, or regression workflow.
---

# GPGPU Semantic Oracle Engine Skill

## 1. Objective

Define the executable semantic ground truth for GPU state transitions and produce canonical traces that expose the first divergence between oracle, RTL, runtime, and memory behavior.

## 2. Input Contract

Input is an ISA, launch, or trace intent with config digest, R0 launch descriptor, instruction subset, memory spaces, expected oracle granularity, and target comparison backend.

## 3. ISA Semantic Contract

The ISA contract is primary. For each instruction define:

- input state: PC, active lane mask, predicate state, register operands, memory operands, launch-visible state.
- transformation: per-lane semantics, scalar/vector behavior, mask behavior, exceptions/illegal cases.
- output state: next PC, register writes, predicate/mask updates, memory request/effect, scoreboard-visible completion, trace event.
- unsupported behavior: explicitly rejected opcodes, address spaces, barriers, atomics, or synchronization modes.

Do not edit ISA semantics to match RTL timing artifacts until the architecture contract says the oracle was wrong.

## 4. Oracle State Model

| State | Producer | Consumer |
|---|---|---|
| PC per SIMT group | launch descriptor, branch/divergence rules | fetch/decode oracle, RTL trace diff |
| active lane mask | launch, predicate execution, divergence/reconvergence | instruction semantics, memory coalescing, trace |
| register file | launch initialization, writeback semantics | subsequent instructions, RTL diff |
| scoreboard/dependency graph | instruction issue/completion model when timing-aware | RTL hazard checks, stall attribution |
| memory hierarchy state | memory semantic model, cache/coalescer model when enabled | loads/stores/atomics/fences, memory trace |
| launch state | R0 launch ABI descriptor | kernel entry, IDs, args, memory spaces |
| execution pipeline state | optional cycle model | timing trace, PPA counters |

## 5. Mandatory Five Questions

For every oracle feature answer:

1. What state exists? Name the architectural or timing state being modeled.
2. Who produces it? Launch ABI, decoder, instruction semantic rule, memory model, or timing model.
3. Who consumes it? Next instruction, RTL diff, memory path, runtime, or PPA.
4. How does it change? Define transition rules, ordering, and illegal cases.
5. How do we verify it? Name unit test, oracle trace, cross-backend diff, or first-divergence test.

## 6. Transformation Rules: Warp Execution Model

Semantic execution is ordered by SIMT group event:

```text
fetch PC -> decode -> apply active mask/predicate -> read operands -> execute semantics -> emit effects -> update PC/mask/register/memory state
```

Cycle-aware extensions may model scheduler stalls, scoreboard waits, memory waits, and backpressure, but functional semantics and timing state must remain separable in the trace schema.

## 7. Memory Ordering Model

Define memory semantics before optimization:

| Operation | Required contract |
|---|---|
| load | address space, active lanes, byte enables, return value, fault behavior, ordering scope |
| store | lane mask, byte enables, data merge, visibility, fault behavior |
| atomic | serialization scope, return value, mask restrictions, ordering |
| fence/flush | affected address spaces, host/device visibility, cache/coherence state |
| local/shared memory | CTA/workgroup scope, bank conflict modeling if timing-aware |
| global memory | ordering, coalescing-neutral semantic result, fault model |

Memory timing details belong in timing trace fields, not in the ISA semantic result unless they change legal architectural behavior.

## 8. Divergence Model

The oracle must own:

- branch condition per lane.
- active mask split and reconvergence target.
- PC stack or equivalent reconvergence state.
- join behavior.
- mask state for predicated instructions.
- illegal divergence or unsupported control-flow cases.

Divergence traces must include old PC/mask, branch target/fallthrough, new PC/mask, and reconvergence metadata.

## 9. State Evolution

Oracle state evolves from launch initialization to ordered SIMT events. Each event reads PC/mask/register/memory state, applies instruction and memory semantics, emits a trace record, and updates the next PC, mask, register file, memory state, and optional timing/dependency state.

## 10. Trace Schema

Canonical trace records should include:

| Category | Fields |
|---|---|
| identity | step/cycle, sequence ID, kernel ID, compute core/CU ID, simt_group_id |
| control | PC, next PC, opcode, active lane mask, predicate mask, divergence action |
| registers | source regs/values, destination regs/values, predicate/special register writes |
| memory | op, address space, lane addresses, byte masks, data, tag/source when modeled, response/fault |
| dependencies | scoreboard set/clear, dependency graph edge, stall reason when modeled |
| launch | grid/block IDs, args pointer, local/shared memory base, resource allocation |
| pipeline | fetch/decode/issue/execute/writeback state when cycle-aware |

If a field is omitted, the oracle output must state why it is not needed for the current gate.

## 11. First-Divergence Detection Engine

Workflow:

1. Run the same kernel image, config, args, input memory, and launch shape on oracle and implementation.
2. Normalize traces to canonical records before diffing.
3. Compare architectural effects first: PC/mask, register writes, memory effects, barriers, faults.
4. Compare timing fields only after architectural effects match.
5. Report the first divergent event with producer, consumer, expected state, observed state, and suspected contract.
6. Route the failure to config, runtime R0/R1, RTL SIMT core, memory path, or oracle semantics.

Final memory output is a smoke test, not a sufficient oracle.

## 12. Output Contract: Oracle Output

The oracle must emit:

- instruction trace.
- memory trace.
- SIMT group/warp state trace.
- divergence trace when control flow exists.
- optional timing/stall trace when cycle-aware.
- config digest, runtime ABI descriptor, input memory digest, and command used to reproduce the trace.

## 13. Verification Gate

| Gate | Required proof |
|---|---|
| instruction gate | unit tests for side effects, masks, illegal cases |
| launch gate | oracle consumes R0 descriptor and argument bytes exactly |
| trace gate | trace schema contains fields required by current RTL/memory diff |
| first-divergence gate | known mismatch reports first wrong event, not final symptom |
| memory gate | loads/stores/atomics/fences match memory contract |
| regression gate | reproducer and at least one non-regression case pass after a fix |

## 14. Design Evidence Layer

Use references only as evidence:

| Evidence | Use |
|---|---|
| GPGPU-Sim | behavioral evidence for functional/timing split, kernel descriptor, warp instruction trace, divergence handling |
| Rocket Chip | structural reference for executable monitors, constrained fuzzers, harnesses, trace sinks |
| Vortex/MIAOW | implementation anchors for SimX-like module twins, trace parser/comparator loops |
| XiangShan-NEMU | tradeoff evidence for reference ABI, step comparison, skip/guided execution, checkpointing |
| CUDA/PTX | ISA/ABI constraint for instruction semantics, memory spaces, masks, barriers |

Evidence validates oracle contracts; it must not appear as top-level framework chapters.

## 15. Failure Modes

- Oracle is only a final-output checker and cannot identify first divergence.
- Functional semantics and timing behavior share hidden mutable state.
- Trace interleaving lacks stable SIMT group identity.
- Memory trace drops lane mask, byte enable, address space, or destination register.
- RTL timing behavior is copied into the oracle as semantics.
- Unsupported instructions silently execute with placeholder behavior.
