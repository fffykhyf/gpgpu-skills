# Regression Tracking

Regression tracking prevents repeated failed repairs from being treated as new problems.

## Required Fields

- `failure_signature`
- `previous_verdict`
- `repaired_by`
- `reappeared_in_run`
- `blocked_module`
- `next_required_evidence`
- `same_patch_attempt_count`
- `last_patch_type`
- `last_owner_module`
- `worsened_gates`
- `rollback_required`
- `escalation_policy`

## Rules

- If a failure reappears after the same patch class, escalate the patch owner.
- If evidence is insufficient twice, require additional trace instrumentation.
- If an architecture patch worsens a prior gate, emit `REGRESSION_RISK_UNBOUNDED`.
- If `same_patch_attempt_count` reaches two without improving the decisive
  gate, the next decision must either change owner or explain why escalation is
  unsafe.
- If `worsened_gates` is non-empty after an architecture patch, set
  `rollback_required` unless the decision report proves the regression is
  expected and accepted.
- `escalation_policy` must state when repeated RTL, runtime, architecture, or
  evidence patches escalate to another owner.
