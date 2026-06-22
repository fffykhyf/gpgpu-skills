---
name: gpgpu-memory-path
description: 用于从 GPU_STATE 执行或检查 GPGPU memory hierarchy behavior、cache behavior、bandwidth model、memory requests、responses、fences、ordering 或 memory traces。
---

# GPGPU Memory Execution Model

## Objective

从 canonical state 执行 memory behavior。

```text
input:  GPU_STATE.memory_state + memory_events
output: memory_trace
```

本 skill 只做 memory execution。禁止做 architectural decisions、speculative design、选择 cache policy、改变 memory hierarchy 或优化 scheduling。

## Allowed Scope

允许：

- `GPU_STATE.memory_state` 已编码的 cache behavior。
- memory hierarchy execution。
- bandwidth model。
- load/store/atomic/fence response behavior。
- memory trace validation。

禁止：

- architectural decisions。
- speculative design。
- 新 cache/coalescing policy selection。
- reinterpretation of memory model enums。

## Input Contract

输入必须包含：

- memory state snapshot。
- 来自 runtime、RTL 或 transform-engine simulation 的 memory event list。
- cache policy enum、memory model enum、bandwidth table、outstanding request table。
- source `GPU_STATE` snapshot hash。

event 需要 `GPU_STATE.memory_state` 中缺失字段时必须拒绝。

## Output Contract

输出：

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
| load/store | 使用 state 中的 address-space、mask、byte-enable、ordering rules |
| atomic | 使用 state 中的 fixed atomic serialization rule |
| cache access | 执行 fixed `cache_policy` mapping，不选择 policy |
| miss/fill | 按 table rules 更新 cache/outstanding state |
| bandwidth limit | bandwidth model saturated 时 emit throttle event |
| fence/flush | 按 encoded rule 更新 visibility/order state |
| fault/replay | emit fixed cause enum 和 state snapshot |

## Verification Gate

- 每个 memory trace event 引用 state field 和 rule ID。
- cache behavior 匹配 `GPU_STATE` 中的 fixed policy。
- bandwidth events 来自 explicit bandwidth tables。
- outstanding request tags 在 retire 前唯一。
- 本 skill 不提出 memory optimization。

## Failure Modes

- 根据 workload symptoms 选择新 cache behavior。
- 把 memory trace gaps 当成推断 events 的许可。
- 丢失 lane mask、byte enable、tag 或 destination mapping。
- 解释 performance 而不是输出 memory execution evidence。
- 修改 `GPU_STATE.memory_state` schema。
