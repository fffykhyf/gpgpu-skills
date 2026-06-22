# FIELD_PROVENANCE v1

## Role

`FIELD_PROVENANCE` records where each IR field came from and which pass owns the derivation.

It is required for synthesized fields and recommended for human spec fields.

## Schema

```text
FIELD_PROVENANCE = {
  field_name,
  source_kind,
  source_id,
  derivation_rule,
  owner_skill,
  input_hash
}
```

## Source Kinds

Allowed:

```text
HUMAN_SPEC
USER_CONSTRAINT
DESIGN_PRESET
SOLVER_DERIVED
REPAIR_DERIVED
```

Forbidden:

```text
UNKNOWN
COMMON_GPU_DEFAULT
MODEL_GUESS
IMPLICIT_DEFAULT
```

## Rules

- Synthesized spec fields must never use `UNKNOWN`.
- `DESIGN_PRESET` must name a preset enum and preset library version.
- `SOLVER_DERIVED` must cite a deterministic derivation rule.
- `REPAIR_DERIVED` must cite a `REFINEMENT_REQUEST_IR`.
- Provenance is audit data; it must not change execution semantics.

