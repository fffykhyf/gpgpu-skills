---
name: gpgpu-deterministic-transform-engine
description: Use when GPU_STATE_IR must be mapped through fixed tables into RTL, simulator, runtime, memory, config, PPA, or validation artifact IR without heuristic design inference.
---

# GPGPU Deterministic Transform Engine

## Skill Role

This skill is the table-driven artifact mapping pass.

```text
GPU_STATE_IR -> ARTIFACT_IR | STATE_TO_VALIDATION_IR
```

It turns canonical state into downstream plans and mapping reports.

## Input IR

Input must include:

- `GPU_STATE_IR`
- transform target
- mapping table version
- enum table version

## Output IR

Allowed targets:

| Target | Output |
|---|---|
| `STATE_TO_RTL` | `RTL_MAPPING_IR` |
| `STATE_TO_SIM` | `SIM_BEHAVIOR_IR` |
| `STATE_TO_RUNTIME` | `RUNTIME_CONTRACT_IR` |
| `STATE_TO_MEMORY` | `MEMORY_MODEL_IR` |
| `STATE_TO_CONFIG` | `CONFIG_BINDING_IR` |
| `STATE_TO_PPA` | counter map and estimation inputs |
| `STATE_TO_VALIDATION` | validation trace schema, required smoke tests, counter binding table, artifact coverage report |

## Allowed Transformations

- Lookup each consumed enum in fixed mapping tables.
- Emit artifact IR containing `GPU_STATE_IR` hash and mapping table version.
- Mark unused state fields explicitly.
- Generate validation plans from consumed fields and trace schemas.

## Forbidden Actions

- Do not infer RTL structure from prose.
- Do not choose cache, scheduler, memory model, or issue policy because it seems better.
- Do not map one enum to multiple implementations.
- Do not generate artifacts from `SPEC_IR` directly.
- Do not hide unmapped state fields.

## Required Invariants

- Every consumed state field is mapped or explicitly unused.
- Every mapped enum has exactly one table entry.
- Every artifact carries state hash and mapping table version.
- `STATE_TO_VALIDATION` includes required smoke tests and artifact coverage.
- Repeated runs with same input are byte-stable.

## Failure Modes

Fail closed when:

- mapping table lacks an enum entry
- one enum maps to multiple implementations
- output omits required state hash
- artifact consumes a field not present in `GPU_STATE_IR`
- validation target cannot be derived from mapped fields

## Report Schema

```text
TRANSFORM_MAPPING_REPORT = {
  gpu_state_hash,
  target,
  mapping_table_version,
  consumed_fields,
  unused_fields,
  missing_mappings,
  emitted_artifacts,
  required_smoke_tests,
  verdict
}
```

`verdict = MAPPED | FAIL_CLOSED`.

## Downstream Contract

Runtime, memory, RTL, golden sim, config, and closure passes may rely on artifact IR only when `TRANSFORM_MAPPING_REPORT.verdict = MAPPED`.
