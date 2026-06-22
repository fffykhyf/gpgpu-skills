---
name: gpgpu-runtime
description: Use when GPU_STATE_IR and runtime contract IR must interpret kernel launch, ABI layout, command queue, fences, completion, or runtime launch smoke behavior.
---

# GPGPU Runtime Execution Semantics

## Skill Role

This skill is the runtime execution semantics pass.

```text
GPU_STATE_IR + RUNTIME_CONTRACT_IR + kernel_launch
  -> execution_trace + runtime_launch_smoke_report
```

It interprets launch behavior. It does not design architecture.

## Input IR

Required inputs:

- `GPU_STATE_IR.launch_state`
- `GPU_STATE_IR.warp_state`
- `GPU_STATE_IR.memory_state` visibility and fence fields
- `GPU_STATE_IR.csr_state`
- `RUNTIME_CONTRACT_IR`
- kernel launch request

## Output IR

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

Also emit:

```text
runtime_launch_smoke_report = {
  module_load,
  argument_layout,
  queue_submit,
  launch_admit,
  warp_start,
  completion_or_fault,
  verdict
}
```

## Allowed Transformations

- Interpret module load using existing kernel image and entry PC.
- Pack arguments according to ABI layout.
- Submit commands while preserving queue order.
- Admit launch only when resources already exist in `GPU_STATE_IR.launch_state`.
- Emit warp start and completion/fault events.

## Forbidden Actions

- Do not infer scheduler policy.
- Do not allocate warps absent from `GPU_STATE_IR`.
- Do not optimize memory visibility.
- Do not modify config defaults.
- Do not treat backend transport as ABI.

## Required Invariants

- Launch trace consumes no fields outside `GPU_STATE_IR` and `RUNTIME_CONTRACT_IR`.
- ABI byte layout is deterministic.
- Queue ordering is preserved.
- Completion and fault are visible in trace.
- Runtime does not choose cache, scheduler, memory, or execution-unit policy.

## Failure Modes

Reject when:

- ABI fields are absent from runtime contract
- kernel image or entry PC is missing from launch state
- launch resources exceed locked state
- command queue ordering cannot be represented
- completion/fault cannot be emitted as a trace event

## Report Schema

`runtime_launch_smoke_report.verdict = PASS | FAIL`.

## Downstream Contract

Closure may use `runtime_launch_smoke_report` for the trace smoke gate. Runtime traces must cite `GPU_STATE_IR` hash and transition rule provenance.
