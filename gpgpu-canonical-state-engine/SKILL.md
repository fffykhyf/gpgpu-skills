---
name: gpgpu-canonical-state-engine
description: Use when locked SPEC_IR must become deterministic GPU_STATE_IR or when canonical GPU state invariants, transitions, snapshots, and FSM APIs must be checked.
---

# GPGPU Canonical State Engine

## Skill Role

This skill is the canonical state construction pass.

```text
SPEC_IR -> GPU_STATE_IR
```

It creates the only execution state truth consumed by runtime, memory, RTL, golden sim, config, and transform passes.

## Input IR

Input must be locked `SPEC_IR` from `gpgpu-spec-lock`.

Reject:

- free-form prose
- `ARCH_CANDIDATE_IR`
- synthesized draft text
- partially locked spec
- missing provenance

## Output IR

Emit:

```text
GPU_STATE_IR = {
  schema_version,
  design_identity,
  source_spec_hash,
  synthesis_candidate_id,
  warp_state,
  scheduler_state,
  memory_state,
  register_state,
  scoreboard_state,
  execution_units,
  execution_pipeline_state,
  launch_state,
  csr_state
}
```

`synthesis_candidate_id` is trace metadata only and must not affect execution semantics.

## Allowed Transformations

Use only FSM API:

| API | Behavior |
|---|---|
| `init(spec_ir)` | Create the initial canonical state. |
| `apply(event)` | Apply one event through a rule table. |
| `transition(rule_id)` | Execute one named transition. |
| `validate_invariants()` | Check state invariants before and after transitions. |
| `snapshot()` | Emit deterministic, serializable, diffable state. |

## Forbidden Actions

- Do not plan architecture.
- Do not evaluate quality.
- Do not select templates.
- Do not absorb candidate-only quality estimates.
- Do not create state fields absent from `SPEC_IR`.
- Do not modify state because RTL or runtime would be easier.

## Required Invariants

- Each valid warp has one PC and one active mask.
- Active mask width equals `SPEC_IR.warp_model.width`.
- Scheduler references only valid resident warps.
- Scoreboard dependencies reference existing registers and owning events.
- Outstanding memory request tags are unique.
- Launch resources do not exceed locked config defaults.
- CSR and fault state are deterministic for the same event sequence.
- `GPU_STATE_IR` contains no candidate-only quality data.

## Failure Modes

Reject when:

- `SPEC_IR` is incomplete
- state schema cannot be fully populated
- transition rule is missing
- invariant fails
- downstream pass asks to reinterpret state

## Report Schema

```text
STATE_ENGINE_REPORT = {
  source_spec_hash,
  gpu_state_hash,
  initialized_fields,
  rejected_fields,
  invariant_results,
  transition_rule_table_version,
  verdict
}
```

`verdict = STATE_EMITTED | REJECTED`.

## Downstream Contract

All downstream passes must consume `GPU_STATE_IR` and may not recover architecture facts from `SPEC_IR`, `ARCH_CANDIDATE_IR`, or prose.
