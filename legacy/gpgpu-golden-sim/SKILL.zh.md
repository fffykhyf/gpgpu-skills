---
name: gpgpu-golden-sim
description: 用于从 GPU_STATE_IR simulator behavior 和 traces 做 deterministic replay、coverage 检查或 first divergence 对比，且不重新定义 ISA semantics。
---

# GPGPU Golden Sim Validator

## Skill Role

本 skill 是 simulator trace validation pass。

```text
GPU_STATE_IR + SIM_BEHAVIOR_IR + simulator_trace
  -> golden_trace_report + property_test_report
```

它验证 simulator artifact，不是第二语义源。

## Input IR

必须输入：

- `GPU_STATE_IR`
- `SIM_BEHAVIOR_IR`
- simulator trace
- mandatory semantic field list

## Output IR

输出：

```text
golden_trace_report = {
  replay_result,
  first_divergence,
  divergent_state_field,
  divergent_rule_id,
  trace_coverage,
  verdict
}
```

同时输出：

```text
property_test_report = {
  deterministic_replay,
  first_divergence_location,
  mandatory_semantic_field_coverage,
  verdict
}
```

## Allowed Transformations

- 根据 `GPU_STATE_IR` transitions replay simulator trace。
- 把 trace events 和声明 trace schema 对比。
- 按 state field 和 rule ID 定位 first divergence。
- 检查 mandatory semantic field coverage。

## Forbidden Actions

- 不重新定义 ISA。
- 不创建 alternate warp model。
- 不修改 simulator semantics 去匹配 RTL。
- 不修改 `GPU_STATE_IR`。
- 不接受缺 mandatory fields 的 traces。

## Required Invariants

- 同一 input trace replay deterministic。
- trace events 引用 state hash 和 mapping version。
- first divergence 可定位到字段。
- mandatory semantic fields 被覆盖。

## Failure Modes

以下情况 reject：

- replay nondeterministic。
- trace 缺 mandatory semantic field。
- first divergence 无法定位。
- simulator event 违反 `GPU_STATE_IR` transition sequence。

## Report Schema

`property_test_report.verdict = PASS | FAIL`。

## Downstream Contract

closure 可用 golden reports 作为 trace smoke 和 divergence gates 的 evidence。golden sim evidence 不能覆盖 `SPEC_IR` 或 `GPU_STATE_IR`。
