---
name: gpgpu-config
description: Use when checking whether GPGPU config_defaults, ABI-visible constants, generated headers, memory maps, launch limits, or capability values are explicitly locked in SPEC_IR and consistently reflected in GPU_STATE.
---

# GPGPU Config Lock Validator

## Objective

Validate config fields already locked by `gpgpu-spec-lock`.

This skill is no longer a schema compiler. It must not derive new config, generate downstream artifacts, choose defaults, or reinterpret architecture.

```text
input:  SPEC_IR.config_defaults + GPU_STATE
output: config_lock_report
```

## Input Contract

Input must include:

- `SPEC_IR.config_defaults`.
- `GPU_STATE` snapshot.
- any generated config artifacts emitted by `gpgpu-deterministic-transform-engine`.

Reject raw parameter lists, prose defaults, or values not present in `SPEC_IR`.

## Output Contract

Emit:

```text
config_lock_report = {
  locked_fields,
  gpu_state_bindings,
  generated_artifact_bindings,
  missing_or_drifted_fields,
  verdict
}
```

## Validation Rules

| Check | Rule |
|---|---|
| default source | every default comes from `SPEC_IR.config_defaults` |
| enum source | every enum is already resolved by `gpgpu-spec-lock` |
| state binding | every config field maps to exactly one `GPU_STATE` field or explicit unused marker |
| artifact binding | generated headers/configs cite transform table version and state hash |
| ABI binding | ABI-visible constants match runtime-visible `GPU_STATE.launch_state` or `csr_state` |

## Forbidden Behavior

- Creating config defaults.
- Deriving hidden values.
- Generating `config.json`, `config.sv`, or `config.h` directly.
- Updating architecture based on config convenience.
- Treating test-only values as canonical state.

## Verification Gate

- No config field exists only in generated artifacts.
- No downstream artifact changes a locked value.
- Missing values route back to `gpgpu-spec-lock`.
- Mapping gaps route to `gpgpu-deterministic-transform-engine`.

## Failure Modes

- Filling missing defaults because previous GPUs use them.
- Letting runtime or RTL define a value not locked in `SPEC_IR`.
- Treating generated config as source of truth.
- Hiding drift behind equivalent-looking names.
