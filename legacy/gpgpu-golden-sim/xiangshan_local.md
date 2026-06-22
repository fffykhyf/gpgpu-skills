# XiangShan-NEMU Local Reference For GPGPU Golden Simulation

This note expands the XiangShan and XiangShan-NEMU references that matter for the `gpgpu-golden-sim` skill. It focuses on reference-model ABI design, step-by-step difftest, skip/guided execution, store-commit events, checkpointing, and first-divergence diagnosis.

Terminology note: XiangShan-NEMU is a RISC-V CPU reference model. Preserve names such as register, CSR, PC, hart, interrupt, and store commit only when discussing the source. For local GPGPU work, translate them to kernel descriptor, SIMT group PC, active lane mask, per-lane registers, barrier state, memory events, fault/replay state, and launch/runtime state.

## What XiangShan-NEMU Teaches For This Skill

The key lesson is that a golden model should be a debuggable reference interface, not just a final-output checker. XiangShan uses NEMU as a shared library reference and compares the DUT step by step through a stable difftest API.

For local GPGPU work, borrow:

- stable reference ABI;
- explicit initialization and state-copy functions;
- step/event comparison;
- skip and guided execution for legal mismatch windows;
- store/memory commit visibility;
- checkpoint and sampled workload support;
- first-divergence reporting.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/xiangshan.md` | Golden-sim lessons and seven-skill mapping. |
| `ref_submodule/xiangshan-nemu/README.md` | NEMU roles: XiangShan reference, standalone profiler, SimPoint/checkpoint generator. |
| `ref_submodule/xiangshan-nemu/src/cpu/difftest/ref.c` | Reference-side exported difftest API. |
| `ref_submodule/xiangshan-nemu/src/cpu/difftest/dut.c` | DUT-side loader, step comparison, skip logic, state synchronization. |
| `ref_submodule/xiangshan-nemu/src/cpu/cpu-exec.c` | Instruction counting, execution loop, profiling statistics. |
| `ref_submodule/xiangshan-nemu/src/isa/riscv64/` | Modular RISC-V ISA implementation. |
| `ref_submodule/xiangshan-nemu/src/memory/` | Physical/virtual memory, host TLB, sparse RAM, store queue wrapper. |
| `ref_submodule/xiangshan-nemu/src/checkpoint/` | Checkpoint, SimPoint, semantic point support. |
| `ref_submodule/xiangshan/README.md` | `make emu ... --diff` flow for XiangShan plus NEMU. |

## Reference-Side ABI

`ref.c` exports functions such as:

- `difftest_memcpy` for reference memory initialization and inspection;
- `difftest_regcpy` and `difftest_csrcpy` for state copy;
- `difftest_exec` for advancing the reference;
- `difftest_status` for pass/fail/state reporting;
- `difftest_guided_exec` for controlled execution;
- interrupt injection and event overflow helpers;
- store commit and branch log query;
- uarch status sync/copy.

Local GPGPU translation:

- memory copy becomes global/shared/local memory initialization and snapshot;
- register copy becomes per-SIMT-group architectural registers, predicate registers, active lane mask, and PC;
- CSR copy becomes runtime/control state, kernel descriptor, capability fields, and fault state;
- store commit becomes memory event comparison;
- guided execution becomes explicit support for relaxed ordering or legal model mismatch windows.

## DUT-Side Adapter

`dut.c` loads the reference `.so` through `dlopen`, resolves difftest symbols, initializes the reference, copies memory/register state, executes the reference, reads back state, and checks register divergence.

Local rule: the RTL testbench or timing simulator should not reach into golden-model internals. It should call a stable adapter with clear operations:

- initialize program and memory image;
- initialize kernel launch descriptor;
- step to next comparable event;
- export state and memory event;
- compare and report first divergence;
- skip or mask explicitly documented legal differences.

## Step Boundary

CPU XiangShan compares instruction-level architectural steps. A GPGPU may need different event boundaries:

- SIMT group instruction issue or commit;
- per-lane register writeback;
- active lane mask update;
- memory request acceptance;
- memory response/writeback;
- barrier arrival/release;
- atomic serialization point;
- fault/replay event;
- CTA/workgroup completion.

The skill should require each new golden model to name its comparison boundary.

## Skip And Guided Execution

XiangShan-NEMU has mechanisms such as skip-ref, skip-dut, and guided execution because a fast RTL or reference may legally behave differently around special events. For local GPGPU use:

- do not silently ignore mismatches;
- write a skip reason, scope, and end condition;
- preserve enough trace to audit skipped events;
- use relaxed comparison only for explicitly unordered behavior.

## Checkpoints And Long Workloads

The NEMU README and `src/checkpoint/` show checkpoint and SimPoint flows for large workloads. This matters for GPGPU kernels that are too long for full RTL or detailed timing simulation.

Local rule:

- keep input image, config, checkpoint, and sample weight together;
- verify a checkpoint resumes into the same golden state;
- label sampled PPA as sampled, not full-run proof.

## Caveats

- Do not use NEMU's RISC-V instruction implementation as a GPGPU ISA reference unless the local ISA is RISC-V-based.
- Do not force CPU instruction commit ordering onto GPU memory, atomics, or barriers without a local memory model.
- Do not compare only final output when intermediate state or event difftest is possible.
