---
name: gpgpu-causal-trace-analyzer
description: Use when explaining GPGPU performance deltas, warp stalls, memory bottlenecks, scheduling inefficiency, or execution-trace changes by mapping observed effects back to GPU_STATE transition causes.
---

# GPGPU Causal Trace Analyzer

## Objective

Convert trace deltas into state-transition causes.

This skill is not a metrics reporter. It must not invent design changes, tune architecture, or summarize counters without causality.

```text
performance_delta -> state_transition_cause
```

## Input Contract

Input must include:

- baseline `GPU_STATE` snapshot.
- variant `GPU_STATE` snapshot or same state with different event trace.
- runtime trace, memory trace, RTL hardware trace, or transform-engine PPA estimate.
- metric delta to explain.
- event ordering and config/spec IDs.

Reject inputs without a baseline, variant, trace identity, or state snapshots.

## Output Contract

Emit a causal report:

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

Every explanation must follow:

```text
metric delta
  -> trace event delta
  -> GPU_STATE field delta
  -> transition(rule_id)
  -> root cause
```

If the chain breaks, report insufficient evidence.

## Required Analyses

| Analysis | Required mapping |
|---|---|
| warp stall cause tracing | stall cycles -> scheduler_state.blocked_set -> dependency/memory/barrier rule |
| memory bottleneck attribution | latency/bandwidth delta -> memory_state queue/cache/outstanding/fence transition |
| scheduling inefficiency root cause | issue-rate delta -> scheduler policy transition and ready/blocked set |
| execution-unit pressure | utilization delta -> execution_units occupancy and completion events |
| launch overhead | runtime delay -> launch_state queue/admission/completion transitions |

## Classification Enums

Use fixed cause enums:

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

Do not create new cause names without updating the enum table.

## Verification Gate

- Baseline and variant traces use the same `SPEC_IR` identity unless the delta explicitly studies spec changes.
- Every reported cause cites a trace event and `rule_id`.
- Root cause is one of the fixed enums.
- Missing evidence is reported as `TRACE_INSUFFICIENT`, not guessed.

## Failure Modes

- Reporting speedup or slowdown without a transition chain.
- Treating a counter name as a root cause.
- Blaming memory when scheduler state shows no ready warp.
- Blaming scheduler when memory outstanding table is saturated.
- Producing recommendations instead of causal attribution.
