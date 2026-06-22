---
name: gpgpu-golden-sim
description: Use when GPU_STATE_IR simulator behavior and traces must be replayed, checked for deterministic coverage, or compared for first divergence without redefining ISA semantics.
---

# GPGPU Golden Sim Validator

## Skill Role

This skill is the simulator trace validation pass.

```text
GPU_STATE_IR + SIM_BEHAVIOR_IR + simulator_trace
  -> golden_trace_report + property_test_report
```

It validates simulator artifacts. It is not a second semantics source.

## Input IR

Required inputs:

- `GPU_STATE_IR`
- `SIM_BEHAVIOR_IR`
- simulator trace
- mandatory semantic field list

## Output IR

Emit:

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

Also emit:

```text
property_test_report = {
  deterministic_replay,
  first_divergence_location,
  mandatory_semantic_field_coverage,
  verdict
}
```

## Allowed Transformations

- Replay simulator trace against `GPU_STATE_IR` transitions.
- Compare trace events to declared trace schema.
- Locate first divergence by state field and rule ID.
- Check mandatory semantic field coverage.

## Forbidden Actions

- Do not redefine ISA.
- Do not create an alternate warp model.
- Do not modify simulator semantics to match RTL.
- Do not modify `GPU_STATE_IR`.
- Do not accept traces lacking mandatory fields.

## Required Invariants

- Same input trace replays deterministically.
- Trace events cite state hash and mapping version.
- First divergence is field-addressable.
- Mandatory semantic fields are covered.

## Failure Modes

Reject when:

- replay is nondeterministic
- trace omits mandatory semantic field
- first divergence cannot be located
- simulator event violates `GPU_STATE_IR` transition sequence

## Report Schema

`property_test_report.verdict = PASS | FAIL`.

## Downstream Contract

Closure may use golden reports for trace smoke and divergence gates. Golden sim evidence must not override `SPEC_IR` or `GPU_STATE_IR`.
