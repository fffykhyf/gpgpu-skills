---
name: gpgpu-golden-sim
description: Use when designing or debugging a GPGPU golden simulator, SimX-like module twin, instruction semantics, trace schema, RTL-vs-simulator comparison, execution mismatch, first divergence, or regression workflow.
---

# GPGPU Golden Simulator

## Overview

Use this skill when simulator behavior, instruction semantics, or trace comparison is the source of truth. The simulator should be an executable twin of the architecture and a practical oracle for RTL debug, not just a final-output checker. Use Rocket Chip as the reference for supplementing ISA or timing oracles with executable protocol monitors, constrained fuzzers, unit-test harnesses, and trace/resource checks. Use XiangShan-NEMU as the reference for a stable reference-model ABI, step-by-step difftest, skip/guided execution, store-commit events, checkpointing, and first-divergence diagnosis.

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

Functional semantics and timing behavior must stay separate. If the timing model or RTL shares structures with the functional oracle, make the shared schema explicit: kernel descriptor, instruction metadata, active lane mask, memory access, trace identity, and config.

Not every oracle has to be a full GPU simulator. For memory, command queues, MMIO, and interconnect-like paths, define local executable contracts: request/response legality, source/tag lifetime, address alignment, mask correctness, ordering, replay, fault, and completion checks.

## Terminology Contract

Use canonical trace terms in schemas and mismatch reports. Keep reference names only when quoting a backend.

| Canonical term | Source aliases | Trace meaning |
|---|---|---|
| SIMT group | warp, wavefront, wave | scheduled execution stream with one PC and active lane mask |
| simt_group_id | warp ID, `wfid`, wave ID, wavefront tag | stable identity used to group trace events |
| active lane mask | active mask, thread mask, `tmask`, `EXEC` mask | lane participation state at an event |
| CTA/workgroup | CTA, block, workgroup | launch/barrier/local-memory scope |
| compute core/CU | core, CU, compute unit | trace source that owns SIMT groups |

## GPGPU-Sim Functional/Timing Split

Use GPGPU-Sim as the reference for separating oracle responsibilities:

| Layer | GPGPU-Sim anchor | Local equivalent |
|---|---|---|
| Functional semantics | `src/cuda-sim/`, `instructions.cc`, `ptx_thread_info` | ISA oracle and architectural state |
| Launch descriptor | `kernel_info_t` | kernel entry, args, grid/block, stream/queue, CTA progress |
| Dynamic instruction event | `warp_inst_t` | issued instruction with SIMT group, PC, active lane mask, operands, memory metadata |
| Divergence state | `simt_stack` | active-mask and reconvergence oracle |
| Timing model | `shader_core_ctx`, `scheduler_unit`, `ldst_unit` | cycle model or RTL trace with stalls and backpressure |
| Trace/debug | `Trace`, stats, component logs | normalized first-divergence artifacts |

Do not edit the functional oracle to match a timing artifact until the architecture contract says the oracle was wrong.

## Rocket Chip Checker Pattern

Use Rocket Chip as the reference for local oracles around protocols and harnesses:

| Checker type | Rocket Chip anchor | Local rule |
|---|---|---|
| protocol monitor | `tilelink/Monitor.scala` | Convert memory/control protocol rules into assertions, not prose. |
| constrained fuzzer | `tilelink/Fuzzer.scala` | Generate legal randomized traffic with source/tag allocation and in-flight tracking. |
| harness oracle | `system/TestHarness.scala`, `unittest/UnitTest.scala` | Give every hardware smoke test start, finish, timeout, memory/debug, and success semantics. |
| trace sink | `trace/` | Emit stable trace records for command, issue, memory, completion, and fault paths. |
| generated docs | docs `mdoc` flow | Keep reference docs and code examples close enough that drift is visible. |

Use these checkers below the full golden simulator. A protocol monitor can catch a bad lane mask or source ID long before a final kernel output differs.

## XiangShan-NEMU Difftest Pattern

Use XiangShan-NEMU as the reference for turning a golden model into a debugging interface:

| Difftest contract | XiangShan-NEMU anchor | Local golden-sim rule |
|---|---|---|
| reference ABI | `src/cpu/difftest/ref.c` | Export stable init, memory copy, state copy, execute, status, interrupt, and event-copy calls. |
| DUT adapter | `src/cpu/difftest/dut.c` | Load the reference model through a stable interface and isolate DUT-specific skip logic. |
| step compare | `difftest_step(pc, npc)` | Compare at an intermediate event boundary before final kernel output. |
| state sync | `difftest_regcpy`, `difftest_csrcpy`, uarch status sync | Define which architectural, control, SIMT, and memory state can be copied or queried. |
| non-identical phases | skip-ref, skip-dut, guided exec | Make legal mismatch windows explicit instead of ignoring failures. |
| long workload support | `src/checkpoint/`, SimPoint workflow | Use checkpoints or sampled regions for long kernels and full-system tests. |

For GPGPU work, translate register/CSR copy into kernel launch state, SIMT group PC, active lane mask, registers, predicate state, barrier state, shared/global memory, memory commit, fault, and replay events. Final output comparison is a smoke test, not a complete oracle.

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
| control | launch or kernel ID, PC, next PC, opcode, active lane mask, predicate mask |
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
6. Run applicable local protocol monitors or harness assertions so legality bugs are separated from semantic mismatches.
7. Report the first divergent event with enough context to reproduce it.
8. Decide whether simulator, RTL, memory path, runtime, config, protocol monitor, or test harness violated the contract.

Do not edit the simulator merely to match RTL output. First decide which side violates the architecture contract. Trace comparison must also:

- Normalize external traces before comparison; never diff raw simulator logs with RTL logs.
- Keep per-SIMT-group streams or stable identity fields so interleaving does not hide the first divergence.
- Distinguish content differences from missing trace or hang conditions.
- Trace architectural side effects first: register writes, special register writes, memory load/store effects, branch, barrier, waitcnt, and retire PC.
- Record the external oracle version, command, input memory, instruction memory, and launch/config files.
- For memory/control paths, include protocol legality state: source/tag allocation, outstanding count, address/mask alignment, replay/nack/fault, and completion ordering.

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains the SimX executable twin and module-aligned simulator/RTL contracts.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the Multi2Sim trace flow, trace parser, tracemon data structures and print functions, trace comparator, regression runner, and what MIAOW's oracle does not prove.

For deeper GPGPU-Sim background tied to this skill, read `gpgpusim_local.md` in this directory. It explains the `cuda-sim` functional oracle, timing model, shared `kernel_info_t`/`warp_inst_t` abstractions, trace schema, and functional-versus-timing caveats.

For Rocket Chip background tied to this skill, read `../../ref/skillref/rocket.md` and then inspect `../../ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala`, `tilelink/Fuzzer.scala`, `unittest/UnitTest.scala`, `system/TestHarness.scala`, and `trace/` when needed.

For XiangShan background tied to this skill, read `xiangshan_local.md` in this directory. It explains the NEMU reference/DUT difftest APIs, step comparison, skip/guided execution, store commit, checkpoint/SimPoint flow, and how to translate those ideas into GPGPU intermediate-state comparison.

## Common Mistakes

- Comparing only final memory output when the first wrong writeback happened earlier.
- Adding trace fields only after a bug appears instead of defining a minimal trace contract early.
- Mixing functional correctness and timing fidelity in one unclear trace.
- Keeping simulator structure unrelated to RTL, making trace diffs hard to map back.
- Letting timing-model convenience code become the ISA oracle.
- Declaring a fix without rerunning the reproducer and at least one regression.
- Waiting for a full-kernel mismatch when a protocol monitor could have caught the invalid request at the source.
- Using random traffic that does not respect legal source/tag, mask, ordering, and in-flight rules.
- Comparing only final memory output when a XiangShan-style difftest boundary could expose the first divergent SIMT, memory, barrier, or fault event.
