# Regression Tracking

Regression tracking prevents repeated failed repairs from being treated as new problems.

## Required Fields

- `failure_signature`
- `previous_verdict`
- `repaired_by`
- `reappeared_in_run`
- `blocked_module`
- `next_required_evidence`

## Rules

- If a failure reappears after the same patch class, escalate the patch owner.
- If evidence is insufficient twice, require additional trace instrumentation.
- If an architecture patch worsens a prior gate, emit `REGRESSION_RISK_UNBOUNDED`.
