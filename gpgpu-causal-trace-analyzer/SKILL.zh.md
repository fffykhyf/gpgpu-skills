---
name: gpgpu-causal-trace-analyzer
description: 用于解释 GPGPU performance deltas、warp stalls、memory bottlenecks、scheduling inefficiency 或 execution-trace changes，并把 observed effects 映射回 GPU_STATE transition causes。
---

# GPGPU Causal Trace Analyzer

## Objective

把 trace delta 转换成 state-transition cause。

本 skill 不是 metrics reporter。禁止发明设计修改、调参架构，或在没有因果链时总结 counters。

```text
performance_delta -> state_transition_cause
```

## Input Contract

输入必须包含：

- baseline `GPU_STATE` snapshot。
- variant `GPU_STATE` snapshot，或同一 state 的不同 event trace。
- runtime trace、memory trace、RTL hardware trace 或 transform-engine PPA estimate。
- 要解释的 metric delta。
- event ordering 和 config/spec IDs。

缺 baseline、variant、trace identity 或 state snapshots 时必须拒绝。

## Output Contract

输出 causal report：

```text
CAUSAL_TRACE = {
  observed_delta,
  affected_state,
  transition_chain,
  root_cause,
  confidence,
  required_followup_trace
}
```

## Cause Mapping Rules

每个解释必须遵循：

```text
metric delta
  -> trace event delta
  -> GPU_STATE field delta
  -> transition(rule_id)
  -> root cause
```

链条断裂时报告 insufficient evidence。

## Required Analyses

| Analysis | Required mapping |
|---|---|
| warp stall cause tracing | stall cycles -> scheduler_state.blocked_set -> dependency/memory/barrier rule |
| memory bottleneck attribution | latency/bandwidth delta -> memory_state queue/cache/outstanding/fence transition |
| scheduling inefficiency root cause | issue-rate delta -> scheduler policy transition and ready/blocked set |
| execution-unit pressure | utilization delta -> execution_units occupancy and completion events |
| launch overhead | runtime delay -> launch_state queue/admission/completion transitions |

## Classification Enums

固定 cause enums：

- `SCHED_SCOREBOARD_WAIT`
- `SCHED_NO_READY_WARP`
- `SCHED_POLICY_LOSS`
- `MEM_CACHE_MISS`
- `MEM_BANK_CONFLICT`
- `MEM_BANDWIDTH_LIMIT`
- `MEM_ORDERING_FENCE`
- `EXEC_UNIT_BUSY`
- `LAUNCH_QUEUE_DELAY`
- `TRACE_INSUFFICIENT`

不更新 enum table 时禁止创造新 cause name。

## Verification Gate

- baseline 和 variant trace 使用相同 `SPEC_IR` identity，除非明确研究 spec changes。
- 每个 cause 都引用 trace event 和 `rule_id`。
- root cause 必须来自 fixed enums。
- 缺 evidence 时报告 `TRACE_INSUFFICIENT`，不能猜。

## Failure Modes

- 没有 transition chain 就报告 speedup/slowdown。
- 把 counter name 当成 root cause。
- scheduler state 显示 no ready warp 时却归因 memory。
- memory outstanding table saturated 时却归因 scheduler。
- 输出 recommendation 而不是 causal attribution。
