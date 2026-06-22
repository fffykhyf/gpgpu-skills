# XiangShan Local Reference For GPGPU Runtime

This note expands the XiangShan references that matter for the `gpgpu-runtime` skill. It focuses on build/run commands, difftest launch, reset/debug/trace/perf ports, virtual devices, full-system images, xspdb, checkpointing, and the separation between debug bring-up and public runtime ABI.

Terminology note: XiangShan runtime material is CPU full-system bring-up, not a GPU driver stack. Preserve names such as reset vector, hartId, CLINT, MSI, NEMU, Difftest, and xspdb when discussing XiangShan. In local GPGPU runtime work, translate the lesson to kernel descriptor, queue/doorbell, command/status registers, completion, fault, trace, perf, and checkpoint controls.

## What XiangShan Teaches For This Skill

XiangShan is useful because it documents how a hardware project is built, run, debugged, and compared against a reference model. The local lesson is to make every runtime path reproducible and to separate public launch ABI from debug/test bring-up hooks.

Borrow these habits:

- exact build and run commands;
- named configs in commands;
- optional golden diff switch;
- reset/debug/trace/perf as stable visible surfaces;
- virtual-device and memory-image setup;
- interactive debug hooks;
- checkpoint and sampled workload flow.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/xiangshan.md` | Runtime lessons and seven-skill mapping. |
| `ref_submodule/xiangshan/README.md` | `make verilog`, `make emu`, `CONFIG`, `EMU_THREADS`, `--diff`, `xspdb` examples. |
| `ref_submodule/xiangshan/ready-to-run/` | Prebuilt images and reference `.so` style runtime assets. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/XSCore.scala` | reset vector, hartId, MSI, clintTime, trace, perf, debugTopDown, critical error ports. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/XSTile.scala` | tile-level memory/MMIO, interrupt, debug, trace, L2, powerdown ports. |
| `ref_submodule/xiangshan/src/main/scala/device/` | Virtual devices such as memory, UART, PLIC, CLINT, timer, flash, debug wrapper. |
| `ref_submodule/xiangshan/src/main/scala/system/SoC.scala` | SoC-level integration and external resources. |
| `ref_submodule/xiangshan-nemu/README.md` | NEMU reference mode, standalone mode, full-system workloads, SimPoint/checkpoint flow. |
| `ref_submodule/xiangshan-nemu/src/checkpoint/` | Checkpoint, SimPoint, semantic point support. |

## Build And Run Contract

The XiangShan README shows build/run commands such as:

- generate Verilog with `make verilog`;
- build Verilator emulator with `make emu`;
- choose configs with `CONFIG=...`;
- set emulator threads with `EMU_THREADS=...`;
- run with `--diff ./ready-to-run/riscv64-nemu-interpreter-so`;
- debug with xspdb commands such as load, watch commit PC, step, and inspect PC.

For local GPGPU runtime documentation, every backend should have:

- build command;
- run command;
- config name;
- program or kernel image path;
- argument and memory setup;
- optional golden/diff switch;
- trace/perf/debug switch;
- expected completion/fault path.

## Visible Control State

`XSCore.scala` and `XSTile.scala` expose runtime-visible and debug-visible signals:

- reset_vector and hartId;
- MSI and timer inputs;
- wfi/powerdown/critical error;
- traceCoreInterface;
- debugTopDown;
- perfEvents;
- L2 hint/miss and cache hierarchy status;
- memory/MMIO interfaces and interrupt lines.

For local GPGPU runtime, expose equivalent concepts:

- reset/program-load path;
- kernel launch descriptor or queue entry;
- doorbell/start;
- completion/event/interrupt;
- fault/status;
- trace/perf snapshot;
- debug stop/step/watch when needed;
- memory/MMIO mapping and capability query.

## Virtual Devices And Full-System Context

The `device/` directory includes virtual memory, timers, interrupt controllers, UARTs, flash, debug wrappers, and other SoC support. This is not a GPU runtime, but it shows that simulator runtime depends on an environment, not just a compute kernel.

Local rule:

- distinguish kernel ABI from simulator environment;
- keep test devices and debug wrappers separate from public API;
- document memory image, MMIO map, and completion convention;
- keep host-side test harness and device-side command ABI synchronized through generated or documented constants.

## Difftest And Checkpoint Flow

XiangShan can run with NEMU as a reference `.so`. NEMU also supports standalone profiling, SimPoint BBV generation, clustering, checkpoint generation, and checkpoint replay.

For a local GPGPU runtime:

- runtime tests should allow golden diff on/off;
- long workloads should have checkpoint or sampled-region support before becoming performance evidence;
- checkpoint metadata must include config, kernel, memory image, launch descriptor, and expected resume point.

## Caveats

- Do not use XiangShan CPU boot flow as GPU kernel launch ABI.
- Do not expose debug-only reset/xspdb/testbench hooks as public runtime API.
- Do not treat NEMU full-system RISC-V support as GPU driver support.
- Borrow reproducible run/debug/diff/checkpoint discipline, not CPU-specific startup semantics.
