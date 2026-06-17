---
name: gpgpu-runtime
description: Use when designing, editing, or reviewing GPGPU runtime, host/device launch, driver API, command queue, MMIO or DCR control, doorbell, DMA, buffer, module, kernel handle, kernel entry, args, grid/block/CTA dispatch, event, fence, cache flush, or synchronization behavior.
---

# GPGPU Runtime

## Overview

Use this skill when host software, launch ABI, command submission, or kernel entry behavior defines the system boundary. Runtime work should turn a testbench-driven core into a reusable device interface without exposing RTL internals as public API.

## Core Rule

Define the launch contract before building features around it:

- how the program or module is loaded
- how the kernel entry PC is selected
- how arguments are staged and addressed
- how grid, block, warp, thread, and CTA IDs are derived
- how memory buffers move between host and device
- how start, completion, fence, event, and cache flush are observed
- which parts are public API, backend transport, and test-only scaffolding

No formal runtime interface should depend on poking internal RTL signals.

## Minimal Launch State Machine

1. Open device or simulator backend.
2. Allocate or map device buffers.
3. Load program/module and resolve kernel entry.
4. Stage kernel arguments.
5. Program grid/block/CTA dimensions and local memory size.
6. Submit launch through a queue or explicit start command.
7. Wait for completion with a defined status/event path.
8. Copy results back and release resources.

This can be small, but it must be the same conceptual path for simulator and RTL tests.

## Interface Layers

| Layer | Owns |
|---|---|
| public runtime API | device, buffer, module, kernel, queue, event handles |
| transport HAL | backend open/close, register read/write, host memory allocation |
| command/control plane | queue entries, doorbells, DCR/MMIO writes, DMA, launch, fence, event |
| kernel ABI | entry PC, args pointer, grid/block IDs, CTA state, local memory |
| tests | one launch workload that runs through the public path |

Keep these layers separate so a new backend does not rewrite the API.

## Runtime Verification

Every runtime change needs at least one of:

- host API smoke test.
- simulator launch test.
- RTL-sim launch test.
- trace showing command, launch, and completion ordering.
- negative test for bad args, invalid kernel, queue full, or timeout.

For launch-related changes, prefer one workload that runs through both simulator and RTL backend.

## Common Mistakes

- Treating runtime as a script instead of a hardware/software contract.
- Letting testbench-only signal pokes become the API.
- Changing kernel argument layout without updating simulator, RTL, runtime, and tests.
- Adding async queues or events without ordering and completion semantics.
- Hiding cache flush or fence behavior inside ad hoc test code.

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It summarizes the relevant Vortex design documents and code paths so routine runtime and launch-ABI work does not require re-reading the whole reference tree.
