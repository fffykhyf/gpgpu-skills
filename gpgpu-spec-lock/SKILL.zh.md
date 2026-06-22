---
name: gpgpu-spec-lock
description: 用于把 human GPGPU spec 或 synthesized spec draft 锁成完整、无歧义、有 provenance、无隐式默认值的 SPEC_IR。
---

# GPGPU Spec Lock

## Skill Role

本 skill 是 spec locking pass。

```text
spec.md | synthesized_spec_draft -> SPEC_IR
```

它稳定架构事实，不设计缺失事实。

## Input IR

输入来源：

```text
source_kind = HUMAN_SPEC | SYNTHESIZED_SPEC_DRAFT
```

允许输入：

- human-written `spec.md`
- `gpgpu-architecture-synthesizer` 生成的 synthesized spec draft
- enum tables
- synthesized source 的 field provenance table

## Output IR

输出：

```text
SPEC_IR = {
  schema_version,
  source_kind,
  design_identity,
  ISA,
  warp_model,
  memory_hierarchy,
  scheduling_policy,
  config_defaults,
  ABI_launch_contract,
  provenance
}
```

## Allowed Transformations

- 把 prose 解析成 candidate fields。
- 只根据声明 enum tables resolve fields。
- 把显式 defaults 转成 locked scalar、enum 或 table values。
- 给每个 field 附加 `FIELD_PROVENANCE`。
- 遇到冲突必须 reject，不能二选一。

当 `source_kind = SYNTHESIZED_SPEC_DRAFT` 时，每个生成值必须引用：

```text
USER_CONSTRAINT
DESIGN_PRESET
SOLVER_DERIVED
REPAIR_DERIVED
```

## Forbidden Actions

- 不推断缺失的 warp size、scheduler、memory hierarchy、ISA 或 cache policy。
- 不接受 `UNKNOWN`、`COMMON_GPU_DEFAULT`、`MODEL_GUESS` 或 `IMPLICIT_DEFAULT` provenance。
- 不把 free-form prose 传给 `gpgpu-canonical-state-engine`。
- 不输出 `GPU_STATE_IR`。
- 不因为 draft 来自 synthesizer 就放松要求。

## Required Invariants

- 所有 required fields 存在。
- 所有 enum resolved。
- 所有 defaults explicit。
- 每个 field 都有 provenance。
- `SPEC_IR` 不包含歧义自然语言。
- 同一输入 repeated locking byte-stable。

## Failure Modes

以下情况 reject：

- required field 缺失。
- enum value unresolved。
- provenance 缺失或 forbidden。
- 两个字段冲突。
- synthesized draft 需要推断才能完整。

## Report Schema

```text
SPEC_LOCK_REPORT = {
  source_kind,
  input_hash,
  spec_ir_hash,
  locked_fields,
  rejected_fields,
  missing_fields,
  provenance_failures,
  verdict
}
```

`verdict = LOCKED | REJECTED`。

## Downstream Contract

`gpgpu-canonical-state-engine` 只能消费 `SPEC_IR`，不能消费原始 prose 或 synthesized draft text。
