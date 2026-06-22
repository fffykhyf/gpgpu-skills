---
name: gpgpu-memory-path
description: 用于从 GPU_STATE_IR memory state 和 memory model IR 执行 cache behavior、coalescing、load/store/atomic/fence semantics 或 memory ordering smoke validation。
---

# GPGPU Memory Path Execution Model

## Skill Role

本 skill 是 memory execution model pass。

```text
GPU_STATE_IR.memory_state + MEMORY_MODEL_IR + memory_events
  -> memory_trace + memory_ordering_smoke_report
```

它执行 state 中已有的 memory semantics。

## Input IR

必须输入：

- `GPU_STATE_IR.memory_state`
- `GPU_STATE_IR.warp_state` lane and mask fields
- `MEMORY_MODEL_IR`
- memory events

## Output IR

输出：

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

同时输出：

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

- 执行 load、store、atomic、fence semantics。
- 根据 `MEMORY_MODEL_IR` 应用 warp coalescing rules。
- 从 mapped tables 建模 cache hit/miss/fill behavior。
- 记录 outstanding request tags 和 owners。
- 报告 bank conflicts、ordering violations 和 faults。

## Forbidden Actions

- 不选择 cache policy。
- 不修改 memory hierarchy。
- 不 invent bandwidth model。
- 不重新解释 lane masks。
- 不为规避 hazard 改架构。

## Required Invariants

- 每个 request tag 在 retire 前唯一。
- lane mask width 匹配 warp width。
- byte enable fields 匹配 access size 和 lane mask。
- fence 和 atomic semantics 遵循 locked memory model。
- ordering violations 是 trace events，不是 hidden logs。

## Failure Modes

以下情况 reject：

- memory event 引用 unknown address space。
- coalescing policy 没有 table entry。
- request tag collision。
- fence semantics 缺失。
- atomic owner undefined。
- lane mask 与 warp state 不一致。

## Report Schema

`memory_ordering_smoke_report.verdict = PASS | FAIL`。

## Downstream Contract

closure 可用 memory trace 和 smoke report 作为 trace smoke 和 memory consistency gates 的 evidence。RTL 和 golden sim 必须对齐相同 memory trace schema。
