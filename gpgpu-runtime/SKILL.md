---
name: gpgpu-runtime
description: Use when designing, editing, or reviewing GPGPU runtime, host/device launch, driver API, command queue, MMIO or DCR control, doorbell, DMA, buffer, module, kernel handle, kernel entry, args, grid/block/CTA/workgroup dispatch, event, fence, cache flush, or synchronization behavior.
---

# GPGPU Runtime Skill

## 1. Objective

Split runtime work into R0 launch ABI definition and R1 execution backend so host software transforms launch intent into deterministic GPU launch state without exposing RTL internals.

## 2. Input Contract

Input is a launch/runtime intent with config digest, kernel image expectations, argument model, memory spaces, queue/control-plane needs, target backend, and required synchronization/fault behavior.

## 3. Runtime State Model

Map every runtime decision into canonical GPU state:

| Runtime state | Canonical GPU state |
|---|---|
| device/capability state | config-visible limits, memory map, queue limits, feature bits, version |
| module/kernel state | kernel image, entry PC, instruction memory, symbol table, required resources |
| argument state | argument bytes, alignment, pointer mapping, constant/local/shared memory bindings |
| launch state | grid/block dimensions, CTA/workgroup IDs, SIMT group allocation, local memory size |
| queue state | command records, ordering, doorbell/MMIO/DCR writes, backend admission, dependencies |
| execution state | running/completed/faulted kernel, event/fence, timeout, interrupt/status, cache visibility |

## 4. Mandatory Five Questions

For every runtime change answer:

1. What state exists? Name ABI, queue, launch, memory, completion, or fault state.
2. Who produces it? Host API, loader, queue builder, MMIO writer, backend, or device.
3. Who consumes it? Golden sim, RTL dispatcher, memory path, kernel code, event/fence wait, or PPA.
4. How does it change? Define state transition and ordering semantics.
5. How do we verify it? Name ABI fixture, launch smoke, negative test, trace, or backend diff.

## 5. R0: Launch ABI Contract

R0 must execute before backend-specific runtime work.

| ABI field | Contract |
|---|---|
| kernel image format | image bytes, text/data sections, symbol names, entry PC, required ISA/config version |
| grid/block model | grid dims, block dims, CTA/workgroup IDs, lane/thread IDs, SIMT group partitioning |
| warp dispatch model | simt_group_width, active lane initialization, resident limits, resource allocation |
| argument layout | byte layout, alignment, scalar/pointer encoding, constant memory, local/shared memory metadata |
| memory space mapping | global, shared/LDS, local, constant, MMIO/uncached spaces and host pointer translation |
| synchronization model | barriers, fences, event semantics, cache flush/visibility, completion/fault reporting |
| capability model | queryable limits, feature bits, memory map, queue count/depth, ABI version |

R0 output is a backend-neutral kernel descriptor plus argument and memory fixtures that golden sim and RTL can consume.

## 6. R1: Runtime Execution Layer

R1 may start only after R0 is stable.

| Execution component | Contract |
|---|---|
| command queue | command type, order, dependencies, queue full behavior, cancellation/error handling |
| MMIO/DCR/doorbell | register offsets, reset values, side effects, write ordering, capability exposure |
| kernel dispatch engine | resource admission, CTA/workgroup allocation, SIMT group creation, start state |
| DMA/buffer movement | allocation, copy direction, alignment, ownership, cache visibility |
| event/fence system | wait, signal, timeout, interrupt/status, memory-ordering guarantee |
| completion tracking | success, fault code, first fault event, trace identity, cleanup |
| backend HAL | simulator, RTL sim, FPGA, or device transport behind the same runtime state model |

R1 output is an execution timeline: queue admission, launch start, memory visibility events, completion/fault, and result readback.

## 7. Transformation Rules

Runtime transforms state in this order:

```text
host intent -> R0 ABI descriptor -> backend command -> device launch state -> execution state -> completion/fence state
```

Rules:

- Host API must never poke internal PC, register, scoreboard, or memory signals directly.
- Kernel descriptor must carry entry PC, launch dims, args pointer, resource limits, config digest, and ABI version.
- Queue operations must preserve ordering between memcpy, launch, event, wait, fence, and completion.
- Backend admission must reject oversized CTA/workgroup, missing resources, unsupported ISA/config, and queue full conditions.
- Faults must be visible as runtime state, not only simulator logs or RTL waveforms.

## 8. State Evolution

| Transition | Producer | Consumer | Verification |
|---|---|---|---|
| `closed -> open` | device open/HAL init | runtime API | capability query test |
| `module bytes -> kernel descriptor` | loader | golden sim/RTL backend | ABI fixture compare |
| `args -> packed argument memory` | host API | kernel code/golden sim | layout unit test |
| `launch descriptor -> queue command` | queue builder | backend scheduler | queue trace |
| `queued -> admitted` | backend admission | dispatch engine | capacity negative test |
| `admitted -> running` | doorbell/MMIO/start command | RTL/golden sim | launch smoke |
| `running -> complete/fault` | backend/device | event/fence wait | completion/fault test |
| `complete -> visible results` | fence/cache flush/readback | host API/PPA | result and trace check |

## 9. Output Contract

Runtime work must emit:

- R0 launch ABI document or fixture.
- kernel descriptor schema.
- generated/runtime header for ABI-visible config values.
- command queue and MMIO/DCR contract when R1 exists.
- trace fields for command, launch, admission, completion, fence, and fault.
- negative tests for invalid kernel, bad args, queue full, timeout, or unsupported config when applicable.

## 10. Verification Gate

Minimum gates:

| Gate | Required proof |
|---|---|
| R0 ABI gate | same descriptor and arg bytes consumed by golden sim and at least one backend fixture |
| R1 launch gate | one workload goes through public API, queue/doorbell, completion, and result readback |
| ordering gate | memcpy/launch/event/wait/fence ordering appears in trace |
| capacity gate | oversized launch or queue full produces defined error state |
| fault gate | invalid command, illegal memory, timeout, or forced fault reports stable runtime state |
| cross-backend gate | simulator and RTL backend use the same R0 descriptor where both exist |

## 11. Design Evidence Layer

Use references only as evidence:

| Evidence | Use |
|---|---|
| GPGPU-Sim | behavioral evidence for configure-call, argument staging, kernel descriptor, stream operation, backend admission |
| Rocket Chip | structural reference for command/response, busy/interrupt/fault, resource exposure, test harness boundaries |
| Vortex/MIAOW | implementation anchors for DCR/MMIO launch control, command processors, FPGA bring-up boundaries |
| XiangShan | evidence for reproducible run/debug/difftest/checkpoint workflows, not a GPU ABI template |
| CUDA/PTX | ABI constraint for kernel images, args, launch dimensions, memory spaces, and synchronization |

Framework evidence must validate R0/R1 contracts instead of becoming standalone sections.

## 12. Failure Modes

- Launch ABI and backend execution are mixed, making simulator and RTL consume different descriptors.
- Testbench pokes become the public runtime API.
- Argument layout changes without updating golden sim, RTL, runtime headers, and tests.
- Events/fences exist without ordering or memory-visibility semantics.
- MMIO offsets lack reset value, side effect, version, and negative tests.
- Backend logs show faults but runtime state reports success.
