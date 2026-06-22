---
name: gpgpu-runtime
description: 用于从 GPU_STATE_IR 和 runtime contract IR 解释 kernel launch、ABI layout、command queue、fence、completion 或 runtime launch smoke 行为。
---

# GPGPU Runtime Execution Semantics

## Skill Role

本 skill 是 runtime execution semantics pass。

```text
GPU_STATE_IR + RUNTIME_CONTRACT_IR + kernel_launch
  -> execution_trace + runtime_launch_smoke_report
```

它解释 launch behavior，不设计架构。

## Input IR

必须输入：

- `GPU_STATE_IR.launch_state`
- `GPU_STATE_IR.warp_state`
- `GPU_STATE_IR.memory_state` visibility and fence fields
- `GPU_STATE_IR.csr_state`
- `RUNTIME_CONTRACT_IR`
- kernel launch request

## Output IR

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

同时输出：

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

- 使用已有 kernel image 和 entry PC 解释 module load。
- 按 ABI layout 打包 arguments。
- submit commands 并保持 queue order。
- 只有 resources 已存在于 `GPU_STATE_IR.launch_state` 时才能 admit launch。
- 输出 warp start 和 completion/fault events。

## Forbidden Actions

- 不推断 scheduler policy。
- 不分配 `GPU_STATE_IR` 中不存在的 warps。
- 不优化 memory visibility。
- 不修改 config defaults。
- 不把 backend transport 当 ABI。

## Required Invariants

- launch trace 不消费 `GPU_STATE_IR` 和 `RUNTIME_CONTRACT_IR` 之外的字段。
- ABI byte layout deterministic。
- queue ordering preserved。
- completion 和 fault 在 trace 中可见。
- runtime 不选择 cache、scheduler、memory 或 execution-unit policy。

## Failure Modes

以下情况 reject：

- ABI fields 不在 runtime contract 中。
- launch state 缺 kernel image 或 entry PC。
- launch resources 超过 locked state。
- command queue ordering 无法表示。
- completion/fault 无法作为 trace event 输出。

## Report Schema

`runtime_launch_smoke_report.verdict = PASS | FAIL`。

## Downstream Contract

closure 可用 `runtime_launch_smoke_report` 作为 trace smoke gate 证据。runtime trace 必须引用 `GPU_STATE_IR` hash 和 transition rule provenance。
