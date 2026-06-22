---
name: gpgpu-mode-controller
description: 用于在任何 IR lock、synthesis、transform 或 validation pass 前，把 GPGPU 请求路由成复现、从 0 设计、patch 探索或 trace debug。
---

# GPGPU Mode Controller

## Skill Role

本 skill 是 compiler 入口路由 pass。

```text
user request -> MODE_SELECTION_IR
```

它只选择路径，不检查或修改架构状态。

## Input IR

输入是用户请求和可用 artifact：

- natural-language request
- optional `spec.md`
- optional trace or validation report
- optional patch intent

## Output IR

输出：

```text
MODE_SELECTION_IR = {
  mode,
  input_kind,
  reason,
  next_skill,
  forbidden_next_skills
}
```

允许 mode：

```text
REPRODUCE
DESIGN
```

允许 input kind：

```text
COMPLETE_SPEC
DESIGN_INTENT
PATCH_REQUEST
TRACE_DEBUG
```

## Allowed Transformations

按表路由：

| 请求形态 | `mode` | `input_kind` | `next_skill` |
|---|---|---|---|
| 复现这个 spec | `REPRODUCE` | `COMPLETE_SPEC` | `gpgpu-spec-lock` |
| 从完整 spec 生成 artifact | `REPRODUCE` | `COMPLETE_SPEC` | `gpgpu-spec-lock` |
| 从 0 设计 GPGPU | `DESIGN` | `DESIGN_INTENT` | `gpgpu-design-intent-lock` |
| 设计小型 FPGA GPGPU | `DESIGN` | `DESIGN_INTENT` | `gpgpu-design-intent-lock` |
| 修改 warp size 并分析影响 | `DESIGN` | `PATCH_REQUEST` | `gpgpu-design-intent-lock` 或 `gpgpu-synthesis-closure-engine` |
| 分析 trace 为什么慢或分歧 | `REPRODUCE` | `TRACE_DEBUG` | `gpgpu-causal-trace-analyzer` |

## Forbidden Actions

- 不输出 `DESIGN_INTENT_IR`。
- 不输出 `SPEC_IR`。
- 不输出 `GPU_STATE_IR`。
- 不选择 warp size、scheduler、ISA、cache、memory hierarchy 或 RTL pipeline。
- DESIGN 请求不完整时不能直接路由到 `gpgpu-spec-lock`。
- REPRODUCE 请求不能经过 `gpgpu-architecture-synthesizer`。

## Required Invariants

- `mode` 必须是 `REPRODUCE` 或 `DESIGN`。
- `input_kind` 必须是声明 enum。
- `next_skill` 必须同时匹配 `mode` 和 `input_kind`。
- `forbidden_next_skills` 必须列出禁止的后继 pass。
- `reason` 引用用户意图，而不是 architecture preference。

## Failure Modes

以下情况 reject 或要求澄清：

- 同时请求 REPRODUCE 和 DESIGN 但没有优先级。
- DESIGN 请求既没有完整 spec，也没有可锁定 intent。
- TRACE_DEBUG 请求没有 trace 或 report。
- 路由需要选择架构事实。

## Report Schema

```text
MODE_SELECTION_REPORT = {
  request_hash,
  selected_mode,
  selected_input_kind,
  next_skill,
  forbidden_next_skills,
  rejection_reason
}
```

## Downstream Contract

下一个 skill 只能遵循 `next_skill`。列入 `forbidden_next_skills` 的 pass 不能消费该请求，除非重新生成 `MODE_SELECTION_IR`。
