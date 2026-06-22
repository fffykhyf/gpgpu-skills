---
name: gpgpu-synthesis-closure-engine
description: 用于当 GPGPU 架构候选、SPEC_IR、GPU_STATE_IR、artifact 和验证报告需要被 accept、reject、refine 或标记证据不足时。
---

# GPGPU Synthesis Closure Engine

## Skill Role

本 skill 是 DESIGN 模式的验收 pass。

```text
ARCH_CANDIDATE_IR + SPEC_IR + GPU_STATE_IR + validation reports
  -> SYNTHESIS_ACCEPTANCE_REPORT_IR
```

它不设计架构，只阻止错误 candidate 通过。

## Input IR

必须输入：

- `ARCH_CANDIDATE_IR`
- `SPEC_IR`
- `GPU_STATE_IR`
- transform artifact coverage report
- config report
- runtime launch smoke report
- memory ordering smoke report
- RTL implementability report
- golden trace report
- optional causal refinement evidence

## Output IR

输出：

```text
SYNTHESIS_ACCEPTANCE_REPORT_IR = {
  candidate_id,
  input_hash,
  spec_ir_hash,
  gpu_state_hash,
  hard_constraint_result,
  requirement_coverage_result,
  spec_round_trip_result,
  state_invariant_result,
  artifact_mapping_result,
  config_lock_result,
  trace_smoke_result,
  quality_gate_result,
  stability_result,
  verdict,
  repair_request
}
```

## Allowed Transformations

- 聚合 gate 结果。
- 比较 candidate identity、spec hash 和 state hash。
- 把 failed gates 转成 `repair_request`。
- 把可修复失败路由回 `gpgpu-architecture-synthesizer`。

## Forbidden Actions

- 不修改 `ARCH_CANDIDATE_IR`。
- 不修改 `SPEC_IR`。
- 不修改 `GPU_STATE_IR`。
- 不把缺失 evidence 当成 pass。
- 不设计替代架构。

## Required Invariants

closure report 必须评估：

1. Requirement coverage。
2. Spec round trip。
3. State invariants。
4. Artifact mapping。
5. Config lock。
6. Trace smoke。
7. Quality gate。
8. Stability gate。

v2 最小实现可以只强制前四个 gate，并把其余 gate 标记为 `INSUFFICIENT_EVIDENCE`。

## Failure Modes

- hard correctness failure 输出 `REJECT`。
- 可修复 trace 或 quality failure 输出 `REFINE_REQUIRED`。
- 缺 evidence 输出 `INSUFFICIENT_EVIDENCE`。
- 只有 required gates 全部通过才能 `ACCEPT`。

## Report Schema

`verdict` 只能是：

```text
ACCEPT
REJECT
REFINE_REQUIRED
INSUFFICIENT_EVIDENCE
```

`repair_request` 必须包含 failed gate、已知 affected state field 和可用 evidence trace。

## Downstream Contract

只有 `ACCEPT` report 可作为 DESIGN 模式最终验收。`REFINE_REQUIRED` 必须通过：

```text
gpgpu-synthesis-closure-engine -> gpgpu-architecture-synthesizer
```
