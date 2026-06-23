# Report Generation Rules

This component assembles the unified `SIM_PERF_ATTRIBUTION_REPORT` from
normalized trace, correctness gate, pass/failure evidence, metrics, causal
graph, root cause, toolchain attribution, and regression fingerprint outputs.

## Unified Report Shape

```yaml
sim_perf_attribution_report:
  report_id: string
  mode: FAILURE_ATTRIBUTION_MODE | PASS_EVIDENCE_MODE
  correctness_verdict: CORRECTNESS_PASS | CORRECTNESS_FAIL | PASS_WITH_INSUFFICIENT_EVIDENCE | PASS_WITH_PERFORMANCE_WARNING
  performance_verdict: PERFORMANCE_PASS | PERFORMANCE_WARNING | PERFORMANCE_FAIL | NOT_EVALUATED
  evidence_verdict: EVIDENCE_COMPLETE | EVIDENCE_INCOMPLETE | EVIDENCE_AMBIGUOUS

  first_divergence_report_ref: optional string
  pass_evidence_report_ref: optional string
  performance_metric_ref: optional string
  perf_attribution_graph_ref: optional string
  root_cause_report_ref: optional string
  toolchain_attribution_report_ref: optional string
  trace_coverage_report_ref: optional string
  regression_fingerprint_ref: optional string

  top_bottlenecks:
    - bottleneck_type: string
      contribution_cycles: integer
      affected_modules: list
      affected_contract_paths: list

  rewrite_handoff:
    required: bool
    patch_type: optional string
    target_skill: optional string
    required_revalidation: list

  human_summary:
    short_verdict: string
    primary_reason: string
    next_action: string
```

## Mode-Specific Rules

Failure Attribution Mode:
- include `FIRST_DIVERGENCE_REPORT`
- include `ROOT_CAUSE_REPORT` unless evidence is insufficient
- include rewrite handoff when owner and revalidation route are known

Pass Evidence Mode:
- include `PASS_EVIDENCE_REPORT`
- include `TRACE_COVERAGE_REPORT`
- include `PERFORMANCE_METRIC_IR`
- include `REGRESSION_FINGERPRINT`
- set rewrite handoff to not required unless evidence or performance warnings
  cross configured thresholds

## Human Summary Rules

- `short_verdict` must state pass, fail, insufficient evidence, or performance
  warning.
- `primary_reason` must reference the decisive report or evidence hash.
- `next_action` must name the owner skill when rewrite or evidence repair is
  required.
- Never claim a clean pass when evidence is incomplete.

## XiangShan Report Additions

Failure reports must reference `MISMATCH_PACKAGE` and
`FAILURE_CAPTURE_PACKAGE` when present. Human summaries should state replay
availability, replay command status, absent artifact reasons, suspected owner,
and required revalidation route without exposing full raw traces by default.

Performance reports must reference `WEIGHTED_PERF_REPORT` when a change claims
speedup or regression. The report must state which weighted phases changed,
which TopDown buckets moved, whether correctness diff passed first, and whether
any phase regressed enough to reject the change.
