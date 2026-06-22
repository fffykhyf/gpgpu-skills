---
name: gpgpu-causal-trace-analyzer
description: 用于把失败的 GPGPU validation reports、traces、performance deltas、stalls、bottlenecks 或 divergence evidence 转成结构化 refinement request。
---

# GPGPU Causal Trace Analyzer

## Skill Role

本 skill 是 causal evidence pass。

```text
failed report | trace delta | performance delta -> REFINEMENT_REQUEST_IR
```

它解释失败或性能变化，不直接修复架构。

## Input IR

允许输入：

- failed `VALIDATION_REPORT_IR`
- runtime、memory、RTL 或 golden trace
- `SYNTHESIS_ACCEPTANCE_REPORT_IR`
- performance delta report
- `GPU_STATE_IR` hash 和 transition rule IDs

## Output IR

输出：

```text
REFINEMENT_REQUEST_IR = {
  root_cause,
  affected_state_field,
  failed_gate,
  proposed_repair_type,
  evidence_trace
}
```

## Allowed Transformations

- 把 metric delta 映射到 trace event delta。
- 把 trace event delta 映射到 `GPU_STATE_IR` field。
- 把 affected field 映射到 transition rule ID。
- 归因 warp stalls、memory bottlenecks、scheduler inefficiency、execution-unit pressure 或 launch overhead。
- 只提出 repair type，不编辑架构。

## Forbidden Actions

- 不修改 `ARCH_CANDIDATE_IR`。
- 不修改 `SPEC_IR`。
- 不修改 `GPU_STATE_IR`。
- 不直接修复 synthesizer output。
- 不报告没有 state 或 trace causal chain 的 metrics。

## Required Invariants

- 每个 root cause 引用 evidence trace。
- 每个 affected state field 存在于 `GPU_STATE_IR` 或标记为 `UNKNOWN_FIELD`。
- 每个 failed gate 都具名。
- proposed repair type 只是 advisory。
- 同一 trace evidence 产生稳定 attribution。

## Failure Modes

以下情况 reject 或标记 evidence 不足：

- 没有 evidence trace。
- metric delta 不能关联到 trace events。
- trace event 不能关联到 state field 或 rule ID。
- 多个 root causes 不能 deterministic ranking。

## Report Schema

```text
CAUSAL_TRACE_REPORT = {
  input_hash,
  root_cause,
  affected_state_field,
  failed_gate,
  evidence_trace,
  confidence,
  refinement_request,
  verdict
}
```

`verdict = ATTRIBUTED | INSUFFICIENT_EVIDENCE`。

## Downstream Contract

repair routing 是：

```text
gpgpu-causal-trace-analyzer
 -> gpgpu-synthesis-closure-engine
 -> gpgpu-architecture-synthesizer
```

causal analyzer 不能绕过 closure。
