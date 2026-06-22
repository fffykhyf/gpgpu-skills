---
name: gpgpu-deterministic-transform-engine
description: 用于把 GPU_STATE_IR 通过固定表映射成 RTL、simulator、runtime、memory、config、PPA 或 validation artifact IR，不做启发式设计推断。
---

# GPGPU Deterministic Transform Engine

## Skill Role

本 skill 是 table-driven artifact mapping pass。

```text
GPU_STATE_IR -> ARTIFACT_IR | STATE_TO_VALIDATION_IR
```

它把 canonical state 转成下游 plan 和 mapping report。

## Input IR

输入必须包含：

- `GPU_STATE_IR`
- transform target
- mapping table version
- enum table version

## Output IR

允许 target：

| Target | Output |
|---|---|
| `STATE_TO_RTL` | `RTL_MAPPING_IR` |
| `STATE_TO_SIM` | `SIM_BEHAVIOR_IR` |
| `STATE_TO_RUNTIME` | `RUNTIME_CONTRACT_IR` |
| `STATE_TO_MEMORY` | `MEMORY_MODEL_IR` |
| `STATE_TO_CONFIG` | `CONFIG_BINDING_IR` |
| `STATE_TO_PPA` | counter map and estimation inputs |
| `STATE_TO_VALIDATION` | validation trace schema, required smoke tests, counter binding table, artifact coverage report |

## Allowed Transformations

- 对每个 consumed enum 查固定 mapping tables。
- 输出 artifact IR，并携带 `GPU_STATE_IR` hash 和 mapping table version。
- 显式标记 unused state fields。
- 从 consumed fields 和 trace schemas 生成 validation plans。

## Forbidden Actions

- 不从 prose 推断 RTL structure。
- 不因为看起来更好就选择 cache、scheduler、memory model 或 issue policy。
- 不把一个 enum 映射到多个实现。
- 不直接从 `SPEC_IR` 生成 artifacts。
- 不隐藏 unmapped state fields。

## Required Invariants

- 每个 consumed state field 都 mapped 或 explicit unused。
- 每个 mapped enum 只有一个 table entry。
- 每个 artifact 带 state hash 和 mapping table version。
- `STATE_TO_VALIDATION` 包含 required smoke tests 和 artifact coverage。
- 同一输入 repeated runs byte-stable。

## Failure Modes

以下情况 fail closed：

- mapping table 缺 enum entry。
- 一个 enum 映射到多个实现。
- output 缺 required state hash。
- artifact 消费了 `GPU_STATE_IR` 中不存在的字段。
- validation target 无法从 mapped fields 派生。

## Report Schema

```text
TRANSFORM_MAPPING_REPORT = {
  gpu_state_hash,
  target,
  mapping_table_version,
  consumed_fields,
  unused_fields,
  missing_mappings,
  emitted_artifacts,
  required_smoke_tests,
  verdict
}
```

`verdict = MAPPED | FAIL_CLOSED`。

## Downstream Contract

只有当 `TRANSFORM_MAPPING_REPORT.verdict = MAPPED` 时，runtime、memory、RTL、golden sim、config 和 closure passes 才能依赖 artifact IR。
