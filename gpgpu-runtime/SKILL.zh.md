---
name: gpgpu-runtime
description: 用于把 GPGPU kernel launch、ABI layout、warp execution semantics、command submission、events、fences 或 completion behavior 从 GPU_STATE 解释成 execution trace。
---

# GPGPU Runtime Execution Semantics

## Objective

从 canonical state 解释 runtime 和 launch semantics。

```text
input:  GPU_STATE + kernel_launch
output: execution_trace
```

本 skill 不是 system designer。禁止添加 architecture assumptions、推断 scheduling policy、优化 memory、修改 config defaults 或重新解释 `GPU_STATE`。

## Allowed Scope

只保留：

- kernel launch semantics。
- ABI-visible warp execution semantics。
- ABI definition 和 argument layout interpretation。
- command queue、event、fence、fault、completion semantics。

删除或拒绝：

- architecture assumptions。
- scheduling inference。
- memory optimization。
- backend-specific design choices。

## Input Contract

输入必须包含：

- `GPU_STATE.launch_state`。
- `GPU_STATE.warp_state`。
- `GPU_STATE.memory_state` visibility/fence fields。
- `GPU_STATE.csr_state` runtime-visible status fields。
- kernel image ID、entry PC、arguments、grid/block shape、command queue event。

ABI fields 不在 `GPU_STATE` 中时必须拒绝 launch request。

## Output Contract

输出：

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

每个 trace event 必须引用 consumed `GPU_STATE` snapshot hash 和 transition rule provenance。

## Execution Rules

| Runtime operation | Deterministic interpretation |
|---|---|
| module load | 绑定 launch state 中已有的 kernel image ID 和 entry PC |
| argument pack | 按 ABI state 编码的 byte layout emit |
| queue submit | append command event，保持 queue ordering |
| launch admit | 检查 `GPU_STATE.launch_state` 中已 resolved 的 resource fields |
| warp start | 从已有 warp allocation emit warp start events |
| fence/event wait | 解释 visibility/completion state，不优化 memory |
| completion | 从 state transition result emit success/fault/timeout |

## Verification Gate

- launch trace 不使用 `GPU_STATE` 外字段。
- 同一 launch 的 ABI byte layout deterministic。
- queue ordering 在 trace 中保留。
- faults 和 completion 作为 trace events 可见。
- runtime 不选择 scheduling、cache、memory 或 execution-unit policy。

## Failure Modes

- 用 runtime 补 missing launch defaults。
- 派生 `GPU_STATE` 中不存在的 warp allocation。
- 把 backend transport detail 当成 ABI。
- fault state 只藏在 logs，不进 trace。
- 在 runtime layer 优化 memory visibility。
