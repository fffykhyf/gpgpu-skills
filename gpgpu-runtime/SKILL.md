---
name: gpgpu-runtime
description: Use when designing, editing, or reviewing GPGPU runtime, host/device launch, driver API, command queue, MMIO or DCR control, doorbell, DMA, buffer, module, kernel handle, kernel entry, args, grid/block/CTA/workgroup dispatch, event, fence, cache flush, or synchronization behavior.
---

# GPGPU Runtime

## Overview

Use this skill when host software, launch ABI, command submission, or kernel entry behavior defines the system boundary. Runtime work should turn a testbench-driven core into a reusable device interface without exposing RTL internals as public API. Use Rocket Chip as the reference for boot/reset resources, debug transport, MMIO/resource descriptions, TestHarness wiring, and RoCC-style command/response/memory/busy/interrupt accelerator control. Use XiangShan as the reference for reproducible build/run/difftest commands, reset/debug/trace/perf control surfaces, full-system images, checkpoint workflows, and separation between debug bring-up and public runtime ABI.

## Core Rule

Define the launch contract before building features around it:

- how the program or module is loaded
- how the kernel entry PC is selected
- how arguments are staged and addressed
- how grid, CTA/workgroup, SIMT group, and thread IDs are derived
- how memory buffers move between host and device
- how start, completion, fence, event, and cache flush are observed
- how reset, boot/program load, debug, fault, capability/version, and interrupt/status paths are exposed
- which parts are public API, backend transport, and test-only scaffolding

No formal runtime interface should depend on poking internal RTL signals.

## Terminology Contract

Use canonical runtime terms in APIs, launch records, and ABI docs. Preserve backend names only at the HAL boundary.

| Canonical term | Source aliases | Runtime meaning |
|---|---|---|
| SIMT group | warp, wavefront, wave | execution group launched inside a CTA/workgroup |
| simt_group_id | warp ID, `wfid`, wave ID, wavefront tag | per-launch or per-core identity for a SIMT group |
| active lane mask | active mask, thread mask, `tmask`, `EXEC` mask | initial or runtime lane participation state |
| CTA/workgroup | CTA, block, workgroup | launch group with block/workgroup IDs and local memory |
| compute core/CU | core, CU, compute unit | device execution resource |

## Minimal Launch State Machine

1. Open device or simulator backend.
2. Allocate or map device buffers.
3. Load program/module and resolve kernel entry.
4. Stage kernel arguments.
5. Program grid/block/CTA/workgroup dimensions and local memory size.
6. Submit launch through a queue or explicit start command.
7. Wait for completion with a defined status/event path.
8. Copy results back and release resources.

This can be small, but it must be the same conceptual path for simulator and RTL tests.

## GPGPU-Sim Launch Model

Use GPGPU-Sim as the reference for a software launch path that does not poke RTL internals:

| Runtime step | GPGPU-Sim anchor | Local requirement |
|---|---|---|
| configure launch | `cudaConfigureCallInternal` | capture grid/block, shared/local memory, stream/queue |
| stage args | `cudaSetupArgumentInternal` | record argument bytes, sizes, offsets, and alignment |
| create descriptor | `cudaLaunchInternal`, `kernel_info_t` | resolve kernel entry and create a stable kernel descriptor |
| enqueue work | `stream_operation` | order memcpy, launch, event, wait, and completion |
| backend admission | `gpu->can_start_kernel()`, launch latency | gate launch by capacity, latency, and max concurrent kernels |
| CTA dispatch | `issue_block2core()` | allocate per-core resources and initialize SIMT groups |

A local runtime may use a simpler API than CUDA/OpenCL, but it still needs launch config, argument staging, kernel lookup, queue operation, backend admission, and completion semantics.

## Interface Layers

| Layer | Owns |
|---|---|
| public runtime API | device, buffer, module, kernel, queue, event handles |
| transport HAL | backend open/close, register read/write, host memory allocation |
| command/control plane | queue entries, doorbells, DCR/MMIO writes, DMA, launch, fence, event |
| kernel ABI | entry PC, args pointer, grid/block IDs, CTA/workgroup state, local memory |
| resource/capability plane | version, device properties, memory map, queue limits, debug/perf/trace availability |
| debug/bring-up plane | reset vector or program-load path, debug transport, fault readout, timeout and success reporting |
| tests | one launch workload that runs through the public path |

Keep these layers separate so a new backend does not rewrite the API.

Classify the early control-plane form before changing launch behavior:

| Mode | Allowed use | Risk |
|---|---|---|
| testbench C hook | unit-test setup, direct SGPR/VGPR initialization, fast trace regressions | becomes a fake public API |
| hard dispatcher | resource allocation, SIMT-group tags, VGPR/SGPR/LDS/GDS bases, done/deallocation | config drift with compute core/CU capacity |
| FPGA MMIO control | program load, register/memory init, start, done, memory-service handshake | host offsets drift from RTL decode |

Even the smallest runtime/control plane must define program load, state initialization, dispatch fields, start, done/status, memory service, result readback, and cleanup. Test-only internal pokes must be labeled test-only.

## Rocket Chip Control-Plane Pattern

Use Rocket Chip as the reference for SoC-visible runtime boundaries:

| Pattern | Rocket Chip anchor | Local runtime rule |
|---|---|---|
| boot/reset resource | `bootrom/`, reset vector, `ExampleRocketSystem` | Define how code/data enters the device and what reset state software can rely on. |
| debug transport | `devices/debug/`, DMI/JTAG/SBA | Provide a debug/fault/status path that is not confused with the public launch API. |
| resource exposure | DTS/resource binding, clock/resource files | Expose capabilities, queue limits, memory map, and optional features through a queryable/versioned path. |
| accelerator command | `LazyRoCC.scala` | Model launch/control as command, response, memory access, busy, interrupt, exception, and optional-port semantics. |
| harness connection | `system/TestHarness.scala`, SimAXIMem/debug/success wiring | Keep simulator and RTL tests connected through the same public-facing control concepts. |

RoCC is not a GPU runtime, but its command/response and busy/interrupt/fault discipline is directly useful for a GPGPU command queue or doorbell design.

## XiangShan Runtime And Difftest Pattern

Use XiangShan as the reference for making run and debug paths reproducible:

| Runtime concern | XiangShan anchor | Local runtime rule |
|---|---|---|
| build/run entry | `README.md`, `make verilog`, `make emu`, `--diff` | Document exact simulator, RTL, and difftest launch commands with config names. |
| visible control state | `XSCore.scala`, `XSTile.scala` | Expose reset, start, interrupt/status, fault, trace, perf, and power/debug paths through stable boundaries. |
| full-system devices | `src/main/scala/device/` | Keep virtual devices, MMIO, memory images, and test harness resources separate from kernel ABI. |
| interactive debug | `xspdb`, trace/debug interfaces | Provide repeatable watch, step, status, and trace hooks for bring-up without making them public ABI. |
| reference model launch | XiangShan-NEMU `--diff` flow | Runtime tests should be able to enable/disable golden diff in a controlled way. |
| checkpointing | NEMU checkpoint/SimPoint flow | Long workloads should have checkpoint or sampled-region support before becoming PPA evidence. |

Do not treat XiangShan's CPU boot flow as a GPU kernel ABI. Borrow the command, image, debug, diff, checkpoint, and status discipline for a GPGPU launch path.

## Runtime Verification

Every runtime change needs at least one of:

- host API smoke test.
- simulator launch test.
- RTL-sim launch test.
- trace showing command, launch, and completion ordering.
- negative test for bad args, invalid kernel, queue full, or timeout.
- capacity test for oversized CTA/workgroup, max concurrent kernels, or backend admission failure when those limits exist.
- capability/version test when public resources, queue limits, memory maps, or optional features change.
- debug/fault/status test for invalid command, memory fault, timeout, or forced interrupt when those paths exist.

For launch-related changes, prefer one workload that runs through both simulator and RTL backend.

## Common Mistakes

- Treating runtime as a script instead of a hardware/software contract.
- Letting testbench-only signal pokes become the API.
- Changing kernel argument layout without updating simulator, RTL, runtime, and tests.
- Adding async queues or events without ordering and completion semantics.
- Hiding launch latency, max concurrent kernels, or resource admission in backend-only constants instead of config/runtime-visible behavior.
- Hiding cache flush or fence behavior inside ad hoc test code.
- Adding MMIO registers without owner, reset value, side effect, capability/version, and test-harness coverage.
- Treating debug/JTAG/DMI-style bring-up paths as the same thing as the public kernel launch API.
- Copying XiangShan reset/boot/debug mechanics directly into the GPU runtime instead of defining a kernel descriptor, queue/doorbell, completion, fault, trace, and diff contract.

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains handle-based runtime APIs, command processor control plane, kernel entry, CTA/workgroup dispatch, and launch DCR programming.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains testbench soft dispatch, hard resource dispatch, FPGA AXI-lite control registers, Xilinx SDK command flow, and the boundaries between test hooks and public runtime contracts.

For deeper GPGPU-Sim background tied to this skill, read `gpgpusim_local.md` in this directory. It explains CUDA/OpenCL runtime interception, launch stack handling, `kernel_info_t`, stream operations, functional/performance mode selection, and launch admission.

For Rocket Chip background tied to this skill, read `../../ref/skillref/rocket.md` and then inspect `../../ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala`, `system/ExampleRocketSystem.scala`, `system/TestHarness.scala`, `bootrom/`, `devices/debug/`, and `resources/` when needed.

For XiangShan background tied to this skill, read `xiangshan_local.md` in this directory. It explains XiangShan build/run/difftest flow, reset/debug/trace/perf ports, virtual devices, full-system images, `xspdb`, checkpointing, and how these ideas translate to a GPGPU runtime boundary.
