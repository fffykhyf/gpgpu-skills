# GPGPU-Sim Local Reference For GPGPU Golden Simulator

This note expands the GPGPU-Sim references that matter for the `gpgpu-golden-sim` skill. It focuses on the separation between functional PTX execution and cycle-level timing, shared kernel/warp abstractions, and traceable first-divergence workflows.

Terminology note: this file preserves GPGPU-Sim source names such as `warp`, `warp_inst_t`, `active_mask`, `CTA`, and `shader`. In the skill contract, map them to `SIMT group`, instruction event, active lane mask, CTA/workgroup, and compute core/CU.

## What GPGPU-Sim Teaches For This Skill

GPGPU-Sim has two cooperating models:

- `src/cuda-sim/`: functional PTX parser, IR, instruction semantics, per-thread architectural state, and memory behavior;
- `src/gpgpu-sim/`: cycle-level timing model for shader core, scheduler, scoreboard, LSU, cache, interconnect, L2, and DRAM.

The key lesson is not that every local project should implement PTX. The lesson is that functional correctness and timing fidelity should be separated while sharing explicit schemas for kernel launch, instruction metadata, active masks, memory accesses, and trace records.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/gpgpusim.md` | Golden-sim lessons and caveats. |
| `ref_submodule/gpgpu-sim/src/cuda-sim/cuda-sim.*` | Functional kernel execution and functionalCoreSim. |
| `ref_submodule/gpgpu-sim/src/cuda-sim/ptx_ir.*` | Function, instruction, operand, symbol, and kernel metadata. |
| `ref_submodule/gpgpu-sim/src/cuda-sim/ptx_sim.*` | `ptx_thread_info`, thread state, callstack, PC, register state. |
| `ref_submodule/gpgpu-sim/src/cuda-sim/instructions.cc` | PTX instruction semantic implementations. |
| `ref_submodule/gpgpu-sim/src/abstract_hardware_model.*` | `kernel_info_t`, `warp_inst_t`, active masks, `simt_stack`. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/shader.*` | Timing issue, functional side effects during issue, writeback and scoreboard release. |
| `ref_submodule/gpgpu-sim/src/trace.*` | Component-selective tracing. |

## Functional And Timing Split

| Layer | GPGPU-Sim owner | Local equivalent |
|---|---|---|
| ISA semantics | `instructions.cc`, `ptx_thread_info` | golden instruction model and architectural state |
| launch shape | `kernel_info_t` | kernel descriptor with grid/block/args/entry |
| dynamic instruction event | `warp_inst_t` | traceable issued instruction with SIMT context |
| divergence state | `simt_stack` | SIMT stack/IPDOM/reconvergence model |
| timing behavior | `shader_core_ctx`, `scheduler_unit`, `ldst_unit` | cycle or RTL model with stalls/backpressure |
| trace/debug | `Trace`, stats, component logs | normalized trace schema and first-divergence artifacts |

`issue_warp()` is important because the timing path creates a dynamic instruction event and invokes functional execution for architectural side effects. Locally, this means the timing model or RTL trace should not invent ISA side effects independently from the oracle.

## Trace Schema Lessons

A GPGPU-Sim-inspired trace should preserve:

- kernel name or launch ID;
- stream or queue ID when relevant;
- compute core/CU ID;
- simt_group_id;
- PC and opcode;
- active lane mask;
- destination/source register metadata;
- memory space, address, size, lane mask, byte enables, and response tag;
- scoreboard, barrier, memory wait, replay, or pipeline stall reason when debugging timing.

Keep architectural trace fields separate from timing fields. Compare register/memory/branch effects before scheduler fairness or latency.

## First-Divergence Use

Use GPGPU-Sim as a pattern for staged oracles:

1. Define instruction semantics in the functional oracle.
2. Create a launch descriptor shared by functional and timing backends.
3. Emit ordered architectural side effects.
4. Run timing/RTL with the same config, input memory, and launch shape.
5. Diff architectural effects first.
6. Only after semantic agreement, diff timing events such as stalls, cache hits, and memory latency.

## Caveats

- GPGPU-Sim's oracle is PTX/CUDA-oriented; do not copy PTX behavior into a non-PTX ISA without an explicit compatibility decision.
- Functional simulation mode is not a cycle model.
- Timing simulation counters do not prove RTL correctness.
- SASS trace-driven mode is useful as a workload path, but it is still not a substitute for local ISA/RTL trace contracts.

