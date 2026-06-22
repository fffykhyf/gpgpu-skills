---
name: gpgpu-canonical-state-engine
description: 用于把 locked SPEC_IR 转成 deterministic GPU_STATE_IR，或检查 canonical GPU state invariants、transitions、snapshots 和 FSM API。
---

# GPGPU Canonical State Engine

## Skill Role

本 skill 是 canonical state construction pass。

```text
SPEC_IR -> GPU_STATE_IR
```

它创建 runtime、memory、RTL、golden sim、config 和 transform passes 消费的唯一执行状态真相。

## Input IR

输入必须是 `gpgpu-spec-lock` 锁定后的 `SPEC_IR`。

拒绝：

- free-form prose
- `ARCH_CANDIDATE_IR`
- synthesized draft text
- partially locked spec
- missing provenance

## Output IR

输出：

```text
GPU_STATE_IR = {
  schema_version,
  design_identity,
  source_spec_hash,
  synthesis_candidate_id,
  warp_state,
  scheduler_state,
  memory_state,
  register_state,
  scoreboard_state,
  execution_units,
  execution_pipeline_state,
  launch_state,
  csr_state
}
```

`synthesis_candidate_id` 只能用于追溯，不能影响执行语义。

## Allowed Transformations

只能使用 FSM API：

| API | Behavior |
|---|---|
| `init(spec_ir)` | 创建初始 canonical state |
| `apply(event)` | 通过 rule table 应用一个 event |
| `transition(rule_id)` | 执行一个 named transition |
| `validate_invariants()` | transition 前后检查 invariants |
| `snapshot()` | 输出 deterministic、serializable、diffable state |

## Forbidden Actions

- 不做 architecture planning。
- 不做 quality evaluation。
- 不选择 templates。
- 不吸收 candidate-only quality estimates。
- 不创建 `SPEC_IR` 中不存在的 state fields。
- 不因为 RTL 或 runtime 更容易实现而修改 state。

## Required Invariants

- 每个 valid warp 只有一个 PC 和一个 active mask。
- active mask width 等于 `SPEC_IR.warp_model.width`。
- scheduler 只引用 valid resident warps。
- scoreboard dependencies 引用存在的 registers 和 owning events。
- outstanding memory request tags 唯一。
- launch resources 不超过 locked config defaults。
- 同一 event sequence 下 CSR 和 fault state deterministic。
- `GPU_STATE_IR` 不包含 candidate-only quality data。

## Failure Modes

以下情况 reject：

- `SPEC_IR` 不完整。
- state schema 无法完整填充。
- transition rule 缺失。
- invariant 失败。
- downstream pass 要求重新解释 state。

## Report Schema

```text
STATE_ENGINE_REPORT = {
  source_spec_hash,
  gpu_state_hash,
  initialized_fields,
  rejected_fields,
  invariant_results,
  transition_rule_table_version,
  verdict
}
```

`verdict = STATE_EMITTED | REJECTED`。

## Downstream Contract

所有下游 pass 必须消费 `GPU_STATE_IR`，不能从 `SPEC_IR`、`ARCH_CANDIDATE_IR` 或 prose 中恢复架构事实。
