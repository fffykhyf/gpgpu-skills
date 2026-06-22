---
name: gpgpu-runtime
description: Use when interpreting GPGPU kernel launch, ABI layout, warp execution semantics, command submission, events, fences, or completion behavior from GPU_STATE into an execution trace.
---

# GPGPU Runtime Execution Semantics

## Objective

Interpret runtime and launch semantics from canonical state.

```text
input:  GPU_STATE + kernel_launch
output: execution_trace
```

This skill is not a system designer. It must not add architecture assumptions, infer scheduling policy, optimize memory, change config defaults, or reinterpret `GPU_STATE`.

## Allowed Scope

Keep only:

- kernel launch semantics.
- warp execution semantics visible to the ABI.
- ABI definition and argument layout interpretation.
- command queue, event, fence, fault, and completion semantics.

Delete or reject:

- architecture assumptions.
- scheduling inference.
- memory optimization.
- backend-specific design choices.

## Input Contract

Input must include:

- `GPU_STATE.launch_state`.
- `GPU_STATE.warp_state`.
- `GPU_STATE.memory_state` visibility/fence fields.
- `GPU_STATE.csr_state` runtime-visible status fields.
- kernel image ID, entry PC, arguments, grid/block shape, and command queue event.

Reject launch requests whose ABI fields are absent from `GPU_STATE`.

## Output Contract

Emit:

```text
execution_trace = {
  launch_events,
  abi_events,
  warp_start_events,
  command_queue_events,
  fence_events,
  completion_or_fault_events
}
```

Every trace event must cite the consumed `GPU_STATE` snapshot hash and transition rule provenance.

## Execution Rules

| Runtime operation | Deterministic interpretation |
|---|---|
| module load | bind kernel image ID and entry PC already present in launch state |
| argument pack | emit byte layout exactly as encoded in ABI state |
| queue submit | append command event; preserve queue ordering |
| launch admit | check resource fields already resolved in `GPU_STATE.launch_state` |
| warp start | emit warp start events from existing warp allocation |
| fence/event wait | interpret visibility and completion state; do not optimize memory |
| completion | emit success/fault/timeout from state transition result |

## Verification Gate

- Launch trace uses no fields outside `GPU_STATE`.
- ABI byte layout is deterministic for the same launch.
- Queue ordering is preserved in trace.
- Faults and completion are visible as trace events.
- Runtime never chooses scheduling, cache, memory, or execution-unit policy.

## Failure Modes

- Using runtime code to fill missing launch defaults.
- Deriving warp allocation not present in `GPU_STATE`.
- Treating a backend transport detail as ABI.
- Hiding fault state in logs instead of trace.
- Optimizing memory visibility in the runtime layer.
