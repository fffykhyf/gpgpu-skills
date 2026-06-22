---
name: gpgpu-rtl-simt-core
description: 用于从 GPU_STATE_IR 和 RTL mapping IR 执行或检查 SIMT hardware model，包括 pipeline、scheduler、scoreboard、memory interface 和 implementability report。
---

# GPGPU RTL SIMT Core

## Skill Role

本 skill 是 pure hardware execution model pass。

```text
GPU_STATE_IR + RTL_MAPPING_IR + kernel
  -> cycle_level_simulation + hardware_trace + rtl_implementability_report
```

它实现 mapped state，不重新解释架构。

## Input IR

必须输入：

- `GPU_STATE_IR`
- `RTL_MAPPING_IR`
- kernel or instruction stream
- required trace schema

## Output IR

输出：

```text
hardware_trace = {
  fetch_events,
  decode_events,
  issue_events,
  execute_events,
  writeback_events,
  scoreboard_events,
  memory_interface_events,
  csr_fault_events
}
```

同时输出：

```text
rtl_implementability_report = {
  unsupported_state_fields,
  unmapped_fsm_rules,
  pipeline_hazards,
  scoreboard_conflicts,
  memory_interface_conflicts,
  verdict
}
```

## Allowed Transformations

- 执行 fetch、decode、issue、execute、writeback pipeline rules。
- 应用已从 `GPU_STATE_IR` 映射的 scheduler FSM 和 scoreboard rules。
- 报告 hazards，但不改变 state definitions。
- 通过 `RTL_MAPPING_IR` 绑定 memory interface behavior。

## Forbidden Actions

- 不 reinterpret architecture。
- 不修改 `GPU_STATE_IR`。
- 不添加 execution units。
- 不因为 RTL convenience 改 scheduler。
- 不 silently drop unsupported state fields。

## Required Invariants

- 每个 hardware trace event 引用 state hash 和 mapping version。
- unsupported fields 列入 implementability report。
- scoreboard conflicts 显式。
- pipeline hazards trace-visible。
- memory interface conflicts 不隐藏。

## Failure Modes

以下情况 reject 或标记不可实现：

- state field 缺 RTL mapping。
- FSM rule unmapped。
- scoreboard conflict 无法解决。
- memory interface width 与 mapped request width 冲突。
- trace schema 无法覆盖 required events。

## Report Schema

`rtl_implementability_report.verdict = IMPLEMENTABLE | NOT_IMPLEMENTABLE | INSUFFICIENT_MAPPING`。

## Downstream Contract

closure 使用 `rtl_implementability_report` 作为 artifact mapping、trace smoke 和 prototype credibility gates 的 evidence。
