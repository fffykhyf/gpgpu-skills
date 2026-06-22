---
name: gpgpu-rtl-simt-core
description: Use when executing a pure GPGPU SIMT hardware model from GPU_STATE and a kernel to produce cycle-level simulation, hardware trace, pipeline events, stalls, or writeback traces.
---

# GPGPU RTL SIMT Pure Hardware Execution Model

## Objective

Execute the hardware model implied by `GPU_STATE`.

```text
input:  GPU_STATE + kernel
output: cycle_level_simulation + hardware_trace
```

This skill is a pure implementation layer. It must not reinterpret architecture, modify canonical state, choose scheduling policy, alter memory hierarchy, or invent RTL structures not emitted by `gpgpu-deterministic-transform-engine`.

## Input Contract

Input must include:

- `GPU_STATE` snapshot and hash.
- kernel image and launch identity.
- RTL mapping artifact from `gpgpu-deterministic-transform-engine`.
- fixed trace schema.

Reject direct prose specs, unlocked `SPEC_IR`, or missing transform-engine mappings.

## Output Contract

Emit:

```text
hardware_trace = {
  cycle,
  warp_id,
  pc,
  active_mask,
  scheduler_event,
  pipeline_stage_events,
  scoreboard_events,
  execution_unit_events,
  memory_interface_events,
  writeback_events,
  fault_events
}
```

Also emit cycle-level summary counters only as trace-derived data.

## Execution Rules

| Hardware area | Rule |
|---|---|
| scheduler | execute fixed scheduler mapping from `GPU_STATE.scheduler_state` |
| pipeline | follow mapped fetch/decode/issue/execute/writeback FSM |
| scoreboard | apply dependency rules from `GPU_STATE.register_state` |
| execution units | use fixed latency/port mapping from transform artifact |
| memory interface | emit memory events; do not choose memory behavior |
| CSR/fault | report state-defined control/status behavior |

## Forbidden Behavior

- Reinterpreting architecture.
- Modifying `GPU_STATE`.
- Selecting alternate implementations.
- Filling missing state from common RTL practice.
- Treating waveform convenience as semantic truth.

## Verification Gate

- Every hardware trace event maps to a `GPU_STATE` field and transform table entry.
- Cycle evolution is deterministic for the same input.
- Scheduler and memory behavior are consumed, not invented.
- Hardware trace can be consumed by `gpgpu-causal-trace-analyzer`.

## Failure Modes

- Changing state because an RTL implementation would be easier.
- Adding untracked stall causes.
- Producing trace fields not declared by transform-engine.
- Collapsing cycle-level events into final output only.
- Debugging by prose explanation instead of hardware trace.
