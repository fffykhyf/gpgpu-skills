---
name: gpgpu-memory-path
description: Use when GPU_STATE_IR memory state and memory model IR must execute cache behavior, coalescing, load/store/atomic/fence semantics, or memory ordering smoke validation.
---

# GPGPU Memory Path Execution Model

## Skill Role

This skill is the memory execution model pass.

```text
GPU_STATE_IR.memory_state + MEMORY_MODEL_IR + memory_events
  -> memory_trace + memory_ordering_smoke_report
```

It executes memory semantics already present in state.

## Input IR

Required inputs:

- `GPU_STATE_IR.memory_state`
- `GPU_STATE_IR.warp_state` lane and mask fields
- `MEMORY_MODEL_IR`
- memory events

## Output IR

Emit:

```text
memory_trace = {
  issue_events,
  coalesce_events,
  tag_events,
  miss_events,
  fill_events,
  retire_events,
  fault_events
}
```

Also emit:

```text
memory_ordering_smoke_report = {
  global_load_store,
  shared_memory_access,
  lane_mask,
  byte_enable,
  fence,
  atomic,
  outstanding_request_tag,
  verdict
}
```

## Allowed Transformations

- Execute load, store, atomic, and fence semantics.
- Apply warp coalescing rules from `MEMORY_MODEL_IR`.
- Model cache hit/miss/fill behavior from mapped tables.
- Record outstanding request tags and owners.
- Report bank conflicts, ordering violations, and faults.

## Forbidden Actions

- Do not choose cache policy.
- Do not modify memory hierarchy.
- Do not invent bandwidth model.
- Do not reinterpret lane masks.
- Do not change architecture to avoid hazards.

## Required Invariants

- Every request tag is unique until retired.
- Lane mask width matches warp width.
- Byte enable fields match access size and lane mask.
- Fence and atomic semantics follow locked memory model.
- Ordering violations are trace events, not hidden logs.

## Failure Modes

Reject when:

- memory event references unknown address space
- coalescing policy has no table entry
- request tag collides
- fence semantics are absent
- atomic owner is undefined
- lane mask is inconsistent with warp state

## Report Schema

`memory_ordering_smoke_report.verdict = PASS | FAIL`.

## Downstream Contract

Closure may use memory trace and smoke report for trace smoke and memory consistency gates. RTL and golden sim must align to the same memory trace schema.
