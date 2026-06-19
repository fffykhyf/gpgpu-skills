# XiangShan Local Reference For GPGPU Architecture Design

This note expands the XiangShan references that matter for the `gpgpu-arch-design` skill. It focuses on state ownership, generated parameters, core/tile/memory boundaries, backend organization, LSQ/replay, NEMU difftest, and HPM/TopDown evidence.

Terminology note: XiangShan is an out-of-order RISC-V CPU, not a GPGPU. Preserve XiangShan source names such as hart, frontend, backend, rename, ROB, CSR, and LSQ only when discussing the source. In local GPGPU contracts, translate the lesson to SIMT group, active lane mask, CTA/workgroup, compute core/CU, runtime launch, and kernel ABI terms.

## What XiangShan Teaches For This Skill

XiangShan's main architecture lesson is not "copy this CPU pipeline." It is how to document and implement a complicated microarchitecture so that ownership, configuration, runtime/debug interfaces, difftest, and counters remain connected.

For local GPGPU work, borrow these habits:

- every major state table has an owner;
- generated parameters and derived widths are explicit;
- core/tile/memory/debug/perf interfaces are visible at module boundaries;
- replay, redirect, fault, and exception paths are part of the architecture contract;
- golden/reference comparison has a stable ABI;
- performance claims are tied to HPM/TopDown event ownership.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/xiangshan.md` | Top-level summary and seven-skill mapping. |
| `ref/xiangshan.pdf` | Frontend, Backend, Memory, HPM, Debug chapters for design-document granularity. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/XSCore.scala` | Core composition and frontend/backend/memBlock/debug/perf wiring. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/XSTile.scala` | Tile boundary, L2, memory/MMIO, interrupt, trace, debugTopDown, powerdown ports. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/Parameters.scala` | `XSCoreParameters` feature flags, widths, queue sizes, memory/cache/TLB params. |
| `ref_submodule/xiangshan/src/main/scala/top/Configs.scala` | Named config fragments such as `BaseConfig` and `MinimalConfig`. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/backend/Backend.scala` | Backend ownership, config checks, CtrlBlock/regions/TopDown integration. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/MemBlock.scala` | Backend-memory interface and LSU/LSQ boundary. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/lsqueue/LoadQueueReplay.scala` | Replay cause ownership and priority discipline. |
| `ref_submodule/xiangshan-nemu/src/cpu/difftest/` | Reference/DUT difftest ABI and step comparison. |

## Core And Tile Boundary

`XSCore.scala` is the best architectural boundary reference. It composes frontend, backend, and memBlock, then wires:

- frontend/backend control, redirects, CSR control, SFENCE, TLB CSR, fencei;
- backend/memory LSQ enqueue, load/store commit, memory violation, wakeup, writeback, exception address, store debug;
- perf events from frontend, backend, LSU, and cache hierarchy;
- traceCoreInterface, debugTopDown, critical error, reset vector, hartId, MSI, and timer signals.

For local GPGPU architecture, this maps to a requirement that the compute core boundary must expose:

- SIMT group state owner;
- launch/runtime-visible status;
- memory request and response contracts;
- trace and difftest export points;
- debug and fault status;
- perf counter aggregation.

`XSTile.scala` shows the next boundary out: core plus L2/top-level memory, MMIO, CHI, interrupt, trace, debugTopDown, critical error, and powerdown. For a GPGPU, the equivalent is compute core/CU plus cache/shared memory/interconnect/runtime control and capability/status ports.

## Backend Ownership

`Backend.scala` and `BackendParams.scala` show a disciplined split between control, datapath, issue, execution units, register files, writeback, ROB/trace/CSR, and TopDown event generation. The local GPGPU rule is not to add ROB or rename. The rule is to define separate owners for:

- SIMT group lifecycle;
- active lane mask and divergence state;
- scheduler readiness;
- scoreboard dependencies;
- operand collection and register file banks;
- FU issue/writeback arbitration;
- LSU/replay/wakeup;
- trace and perf events.

If an architecture proposal cannot name these owners, it is not ready to become RTL work.

## Memory And Replay As Architecture

The PDF memory chapters and `MemBlock.scala` show that memory is a first-class architectural boundary, not a helper under execute. `LSQWrapper.scala` owns load/store queue integration, forwarding, bypass, rollback, uncache/MMIO, hints, debug, and diff hooks. `LoadQueueReplay.scala` makes replay causes explicit and warns that priority changes can deadlock.

For GPGPU architecture proposals, memory features must include:

- request carrier fields: compute core/CU, simt_group_id, active lane mask, address, byte mask, op, space, source/tag;
- replay/fault/stall cause list and priority;
- wakeup and response demux rules;
- counter and trace owner;
- golden comparison boundary.

## NEMU Difftest As Architecture Evidence

`xiangshan-nemu/src/cpu/difftest/ref.c` exports reference-side calls such as memory copy, register/CSR copy, execute, status, guided execution, interrupt injection, store commit, branch log query, and uarch status sync. `dut.c` shows the DUT side loading the reference `.so`, stepping the reference, copying state, and checking the first divergence.

For local architecture, this means a feature is more credible when it defines an intermediate comparison point:

- SIMT group issue/commit trace;
- memory commit/store event;
- active lane mask update;
- barrier/fault/replay event;
- runtime launch descriptor state.

Final output comparison is not enough for complex architecture work.

## HPM And TopDown

The PDF HPM chapter and `TopDownGen.scala` show how XiangShan connects module-local events to top-down bottleneck classes. The useful rule is that every architecture claim should name the event owner and how that event will be rolled up into a performance explanation.

For a GPGPU, translate XiangShan's frontend/backend/memory/cache classes into:

- launch and dispatch;
- scheduler and issue;
- scoreboard and operands;
- SIMT divergence and barriers;
- LSU/coalescer/replay;
- cache/TLB/NoC/DRAM;
- runtime queues and completion.

## Caveats

Do not infer GPGPU semantics from these XiangShan mechanisms:

- branch predictor, FTQ, TAGE/ITTAGE, or RAS;
- rename, ROB, RAB, and CPU precise commit;
- hart/CSR/privileged architecture as GPU kernel ABI;
- CPU cache coherence policy as GPU memory consistency;
- RISC-V NEMU ISA as the local GPGPU ISA unless the local ISA explicitly reuses it.
