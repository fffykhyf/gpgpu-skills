---
name: gpgpu-memory-path
description: Use when executing or checking GPGPU memory hierarchy behavior, cache behavior, bandwidth model, memory requests, responses, fences, ordering, or memory traces from GPU_STATE.
---

# GPGPU Memory Execution Model

## Objective

Execute memory behavior from canonical state.

```text
input:  GPU_STATE.memory_state + memory_events
output: memory_trace
```

This skill is memory execution only. It must not make architectural decisions, speculate about design alternatives, choose cache policy, change memory hierarchy, or optimize scheduling.

## Allowed Scope

Allowed:

- cache behavior already encoded in `GPU_STATE.memory_state`.
- memory hierarchy execution.
- bandwidth model.
- load/store/atomic/fence response behavior.
- memory trace validation.

Forbidden:

- architectural decisions.
- speculative design.
- new cache/coalescing policy selection.
- reinterpretation of memory model enums.

## Input Contract

Input must include:

- memory state snapshot.
- memory event list from runtime, RTL, or transform-engine simulation.
- cache policy enum, memory model enum, bandwidth table, outstanding request table.
- source `GPU_STATE` snapshot hash.

Reject events that require fields missing from `GPU_STATE.memory_state`.

## Output Contract

Emit:

```text
memory_trace = {
  request_events,
  cache_events,
  bandwidth_events,
  response_events,
  fence_ordering_events,
  fault_or_replay_events
}
```

## Execution Rules

| Event | Required behavior |
|---|---|
| load/store | apply address-space, mask, byte-enable, and ordering rules from state |
| atomic | apply fixed atomic serialization rule from state |
| cache access | execute fixed `cache_policy` mapping; do not choose policy |
| miss/fill | update cache/outstanding state by table rules |
| bandwidth limit | emit throttle event when bandwidth model is saturated |
| fence/flush | update visibility/order state exactly as encoded |
| fault/replay | emit fixed cause enum and state snapshot |

## Verification Gate

- Every memory trace event cites a state field and rule ID.
- Cache behavior matches the fixed policy encoded in `GPU_STATE`.
- Bandwidth events are derived from explicit bandwidth tables.
- Outstanding request tags are unique until retired.
- No memory optimization is proposed by this skill.

## Failure Modes

- Choosing a new cache behavior from workload symptoms.
- Treating memory trace gaps as permission to infer events.
- Dropping lane mask, byte enable, tag, or destination mapping.
- Explaining performance instead of emitting memory execution evidence.
- Modifying `GPU_STATE.memory_state` schema.
