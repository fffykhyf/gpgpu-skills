---
name: gpgpu-golden-sim
description: Use when checking simulator traces or semantic behavior artifacts generated from GPU_STATE, especially when validating that simulation follows deterministic transform-engine mappings.
---

# GPGPU Simulator Artifact Validator

## Objective

Validate simulator behavior emitted by `gpgpu-deterministic-transform-engine`.

This skill is no longer an independent semantic oracle. It must not define ISA semantics, invent timing behavior, or modify `GPU_STATE`.

```text
input:  GPU_STATE + SIM_BEHAVIOR + simulator_trace
output: sim_validation_report
```

## Input Contract

Input must include:

- `GPU_STATE` snapshot and hash.
- `STATE_TO_SIM` artifact from `gpgpu-deterministic-transform-engine`.
- simulator trace to validate.
- optional RTL/runtime/memory traces for comparison.

Reject traces that cannot be tied to a state hash and transform table version.

## Output Contract

Emit:

```text
sim_validation_report = {
  matched_events,
  divergent_events,
  missing_trace_fields,
  transform_rule_violations,
  verdict
}
```

## Validation Rules

| Check | Rule |
|---|---|
| state identity | trace cites the same `GPU_STATE` snapshot hash as the sim artifact |
| rule identity | every semantic event cites a transform rule ID |
| field coverage | PC, active mask, register, memory, launch, and fault fields match declared trace schema |
| event order | event order follows the state-machine transition sequence |
| divergence report | first mismatch is reported with expected and observed state |

## Forbidden Behavior

- Defining ISA semantics outside `GPU_STATE`.
- Treating final output as the oracle.
- Editing simulator behavior to match RTL.
- Adding trace fields not declared by the transform engine.
- Resolving ambiguous specs.

## Verification Gate

- All simulator events map to `GPU_STATE` fields and transform rules.
- First divergence is reported before summary metrics.
- Missing trace fields route to `gpgpu-deterministic-transform-engine`.
- Missing semantics route to `gpgpu-spec-lock` or `gpgpu-canonical-state-engine`.

## Failure Modes

- Acting as a second source of truth.
- Comparing raw logs instead of canonical trace records.
- Allowing simulator convenience behavior to override state.
- Hiding divergent events behind aggregate pass/fail.
