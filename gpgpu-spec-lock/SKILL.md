---
name: gpgpu-spec-lock
description: Use when a human GPGPU spec or synthesized spec draft must become complete, unambiguous, provenance-bearing SPEC_IR with no implicit defaults.
---

# GPGPU Spec Lock

## Skill Role

This skill is the spec locking pass.

```text
spec.md | synthesized_spec_draft -> SPEC_IR
```

It stabilizes architecture facts. It does not design missing facts.

## Input IR

Input source kind:

```text
source_kind = HUMAN_SPEC | SYNTHESIZED_SPEC_DRAFT
```

Allowed input:

- human-written `spec.md`
- synthesized spec draft from `gpgpu-architecture-synthesizer`
- enum tables
- field provenance table when source is synthesized

## Output IR

Emit:

```text
SPEC_IR = {
  schema_version,
  source_kind,
  design_identity,
  ISA,
  warp_model,
  memory_hierarchy,
  scheduling_policy,
  config_defaults,
  ABI_launch_contract,
  provenance
}
```

## Allowed Transformations

- Parse prose into candidate fields.
- Resolve fields only against declared enum tables.
- Convert explicit defaults into locked scalar, enum, or table values.
- Attach `FIELD_PROVENANCE` to each field.
- Reject conflicts instead of choosing between them.

When `source_kind = SYNTHESIZED_SPEC_DRAFT`, every generated value must cite:

```text
USER_CONSTRAINT
DESIGN_PRESET
SOLVER_DERIVED
REPAIR_DERIVED
```

## Forbidden Actions

- Do not infer missing warp size, scheduler, memory hierarchy, ISA, or cache policy.
- Do not accept `UNKNOWN`, `COMMON_GPU_DEFAULT`, `MODEL_GUESS`, or `IMPLICIT_DEFAULT` provenance.
- Do not pass free-form prose to `gpgpu-canonical-state-engine`.
- Do not emit `GPU_STATE_IR`.
- Do not relax requirements because the draft came from a synthesizer.

## Required Invariants

- All required fields are present.
- All enums are resolved.
- All defaults are explicit.
- Every field has provenance.
- `SPEC_IR` contains no ambiguous natural language.
- Repeated locking of the same input is byte-stable.

## Failure Modes

Reject when:

- a required field is missing
- enum value is unresolved
- provenance is absent or forbidden
- two fields conflict
- synthesized draft needs inference to become complete

## Report Schema

```text
SPEC_LOCK_REPORT = {
  source_kind,
  input_hash,
  spec_ir_hash,
  locked_fields,
  rejected_fields,
  missing_fields,
  provenance_failures,
  verdict
}
```

`verdict = LOCKED | REJECTED`.

## Downstream Contract

`gpgpu-canonical-state-engine` may consume only `SPEC_IR`, not original prose or synthesized draft text.
