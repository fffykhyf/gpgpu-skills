---
name: gpgpu-golden-sim
description: 用于检查从 GPU_STATE 生成的 simulator traces 或 semantic behavior artifacts，特别是验证 simulation 是否遵循 deterministic transform-engine mappings。
---

# GPGPU Simulator Artifact Validator

## Objective

验证 `gpgpu-deterministic-transform-engine` 输出的 simulator behavior。

本 skill 不再是 independent semantic oracle。禁止定义 ISA semantics、发明 timing behavior 或修改 `GPU_STATE`。

```text
input:  GPU_STATE + SIM_BEHAVIOR + simulator_trace
output: sim_validation_report
```

## Input Contract

输入必须包含：

- `GPU_STATE` snapshot and hash。
- 来自 `gpgpu-deterministic-transform-engine` 的 `STATE_TO_SIM` artifact。
- 待验证 simulator trace。
- optional RTL/runtime/memory traces。

无法绑定 state hash 和 transform table version 的 trace 必须拒绝。

## Output Contract

输出：

```text
sim_validation_report = {
  matched_events,
  divergent_events,
  missing_trace_fields,
  transform_rule_violations,
  verdict
}
```

## Validation Rules

| Check | Rule |
|---|---|
| state identity | trace 引用与 sim artifact 相同的 `GPU_STATE` snapshot hash |
| rule identity | 每个 semantic event 引用 transform rule ID |
| field coverage | PC、active mask、register、memory、launch、fault fields 匹配 declared trace schema |
| event order | event order 遵循 state-machine transition sequence |
| divergence report | first mismatch 报告 expected 和 observed state |

## Forbidden Behavior

- 在 `GPU_STATE` 外定义 ISA semantics。
- 把 final output 当 oracle。
- 为匹配 RTL 修改 simulator behavior。
- 添加 transform engine 未声明的 trace fields。
- 解决 ambiguous specs。

## Verification Gate

- 所有 simulator events 映射到 `GPU_STATE` fields 和 transform rules。
- summary metrics 前先报告 first divergence。
- missing trace fields 路由到 `gpgpu-deterministic-transform-engine`。
- missing semantics 路由到 `gpgpu-spec-lock` 或 `gpgpu-canonical-state-engine`。

## Failure Modes

- 充当第二个 source of truth。
- 比较 raw logs 而不是 canonical trace records。
- 允许 simulator convenience behavior 覆盖 state。
- 用 aggregate pass/fail 隐藏 divergent events。
