---
name: gpgpu-design-intent-lock
description: 用于当 GPGPU 请求是设计目标而不是完整架构 spec 时，锁定从 0 设计意图、preset、workload、平台、约束或验证目标。
---

# GPGPU Design Intent Lock

## Skill Role

本 skill 是 DESIGN 模式的输入稳定 pass。

```text
natural-language design goal -> DESIGN_INTENT_IR
```

它只锁定用户意图，不设计架构。

## Input IR

输入是自然语言设计目标和可选显式 preset。

必须锁定：

- objective
- workload profile
- target platform
- validation target
- hard constraints 或显式 `NONE`

## Output IR

输出：

```text
DESIGN_INTENT_IR = {
  objective,
  non_goals,
  workload_profile,
  target_platform,
  hard_constraints,
  soft_constraints,
  required_features,
  optional_features,
  validation_target,
  prototype_credibility_target,
  preset,
  source_request_hash
}
```

## Allowed Transformations

- 把用户目标归一化成一个明确 objective。
- 提取 workload、platform、constraints 和 validation target。
- 把显式 preset 转成允许的 enum。
- 缺失的 optional features 可以标记为 absent，但不能补架构值。

允许 preset：

```text
MINIMAL_TEACHING_GPGPU
RESEARCH_SIMT_BASELINE
FPGA_SMALL_GPGPU
RTL_SYNTHESIZABLE_BASELINE
GPGPU_WITH_TENSOR_EXTENSION
NONE_EXPLICIT
```

## Forbidden Actions

- 不输出 `SPEC_IR`。
- 不选择 SM count、warp size、cache policy、scheduler、ISA、memory hierarchy、register file size 或 RTL pipeline。
- 不从例子中推断架构。
- 不把未锁定自然语言传给 `gpgpu-architecture-synthesizer`。

## Required Invariants

- objective、workload profile、target platform、validation target 必须显式。
- preset 必须来自允许 enum。
- non-goal 只能保持为负约束，不能转成 feature。
- `DESIGN_INTENT_IR` 不能出现架构字段。

## Failure Modes

以下情况必须 reject：

- 缺 objective。
- 缺 workload profile。
- 缺 target platform。
- 缺 validation target。
- preset 不在允许 enum 中。
- 用户请求需要架构值，但没有足够约束锁定设计意图。

## Report Schema

```text
DESIGN_INTENT_LOCK_REPORT = {
  input_hash,
  locked_fields,
  missing_required_fields,
  rejected_architecture_fields,
  selected_preset,
  verdict
}
```

`verdict = LOCKED | REJECTED | NEEDS_EXPLICIT_PRESET`。

## Downstream Contract

`gpgpu-architecture-synthesizer` 只能消费 `DESIGN_INTENT_IR` 中的锁定字段，不能回读原始自然语言来补架构事实。
