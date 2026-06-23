# Minimal Trace Window Rules

This file defines how correctness and performance windows are selected for
reports and rewrite handoff.

## Correctness Window

Used for RTL/golden mismatch:

```text
window_start = first_divergence_cycle - pre_window
window_end   = first_divergence_cycle + post_window
```

Required contents:
- last matching event
- first mismatching event
- all direct dependency events
- related contract paths
- related RTL module paths
- related toolchain artifact paths when present
- evidence hashes

Default rule:

```yaml
correctness_window_rule:
  pre_events: 8
  post_events: 8
  include_last_matching_event: true
  include_first_mismatching_event: true
  include_dependency_closure: true
  include_contract_path: true
  include_rtl_module_path: true
  include_toolchain_artifact_path: true
```

## Performance Window

Used for bottleneck attribution:

```text
select the continuous window with the highest stall-cycle contribution;
if several windows are close, choose the earliest one with the most complete
evidence.
```

Default rule:

```yaml
performance_window_rule:
  candidate_windows:
    - top_stall_contribution_window
    - sustained_bottleneck_window
    - queue_saturation_window
    - periodic_replay_window
  tie_breakers:
    - highest_evidence_completeness
    - earliest_window
    - strongest_contract_mapping
    - strongest_rtl_module_mapping
```

## Fail-Closed Rules

- Do not expand the window to the whole trace unless causal closure requires it.
- Do not drop direct dependency events to make a window smaller.
- Mark the window `AMBIGUOUS_TRACE_ORDERING` when event order cannot be ranked.
