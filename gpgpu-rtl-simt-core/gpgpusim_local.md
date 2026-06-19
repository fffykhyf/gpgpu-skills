# GPGPU-Sim Local Reference For GPGPU RTL SIMT Core

This note expands the GPGPU-Sim references that matter for the `gpgpu-rtl-simt-core` skill. It focuses on SIMT group state, scheduler readiness, scoreboard ownership, operand collection, issue, writeback, and how to translate C++ timing-model behavior into RTL contracts.

Terminology note: this file preserves GPGPU-Sim source names such as `warp`, `warp_id`, `shd_warp_t`, `active_mask`, `CTA`, and `shader core`. In the skill contract, map them to `SIMT group`, `simt_group_id`, SIMT-group state table, active lane mask, CTA/workgroup, and compute core/CU.

## What GPGPU-Sim Teaches For This Skill

GPGPU-Sim's shader core is a useful state checklist:

- `shd_warp_t` owns resident warp state;
- `simt_stack` owns divergence/reconvergence active masks and PCs;
- `scheduler_unit::cycle()` owns readiness checks and issue selection;
- `scoreboard` owns register dependency checks and release;
- `opndcoll_rfu_t` owns operand collector and register-bank pressure;
- pipeline register sets and FU units own execution availability;
- `writeback()` owns result completion and scoreboard release.

Use these as RTL ownership prompts. Do not copy the C++ control flow literally.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/gpgpusim.md` | SIMT timing-model lessons. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/shader.h` | `shd_warp_t`, scheduler classes, operand collector, execution units, LSU interfaces. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/shader.cc` | fetch/decode/issue/read-operands/execute/writeback behavior. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/scoreboard.*` | Register hazard tracking. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/stack.*` | SIMT stack support. |
| `ref_submodule/gpgpu-sim/src/abstract_hardware_model.*` | `simt_stack`, `warp_inst_t`, active masks, dynamic instruction metadata. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc` | CTA allocation into shader core resources through `issue_block2core()`. |

## Shader-Core Cycle Reference

`shader_core_ctx::cycle()` advances stages in this order:

1. writeback
2. execute
3. read operands
4. issue
5. decode
6. fetch

Local RTL does not need the same physical order, but it must define equivalent stage boundaries and what state is read or written in each stage.

## Scheduler Readiness Checklist

`scheduler_unit::cycle()` checks whether a warp can issue by asking:

- is the warp valid, not done, and not waiting?
- does the instruction buffer contain a decoded instruction?
- does SIMT stack top PC match the instruction PC?
- is the active lane mask non-empty?
- does scoreboard report no register collision?
- is the target FU/pipeline register available?
- does issue width allow another instruction from this SIMT group?
- are barrier, membar, depbar, or outstanding memory conditions blocking?

For RTL, turn these into explicit tables and signals. A single unexplainable `ready` wire is not enough.

## Dynamic Issue Packet

`issue_warp()` constructs a dynamic `warp_inst_t` with:

- active mask;
- warp/SIMT-group ID;
- dynamic warp ID;
- scheduler ID;
- stream ID;
- instruction and PC;
- memory-access metadata when needed;
- latency and execution-pipeline type.

The RTL issue packet should carry the local equivalent: `simt_group_id`, PC, active lane mask, op/FU type, source/destination fields, memory metadata, and enough launch/CTA context for barriers and trace.

## Translating To RTL

| GPGPU-Sim behavior | RTL requirement |
|---|---|
| vector/list of running warps | explicit resident SIMT-group table with reset/valid/done states |
| C++ queue or pipeline register | valid-ready FIFO/register with flush and kill rules |
| function call to `scoreboard.reserveRegisters()` | sequential scoreboard set event tied to issue accept |
| function call to release registers in writeback | scoreboard clear tied to writeback valid and destination |
| C++ SIMT stack update | registered stack/table update with branch/exit/reconvergence tests |
| `waiting()` checks | named wait owners: memory, barrier, branch, membar, depbar, replay |
| pipeline availability method | explicit FU ready/backpressure path |

## Caveats

- GPGPU-Sim can perform functional side effects during timing issue; RTL must separate architectural writeback from combinational scheduling.
- C++ containers hide capacity and reset behavior; RTL must size tables, FIFOs, masks, tags, and counters.
- GPGPU-Sim timing order is a model choice, not automatically an implementation timing path.

