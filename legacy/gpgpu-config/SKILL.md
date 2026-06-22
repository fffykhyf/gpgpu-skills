---
name: gpgpu-config
description: Use when GPGPU config defaults, hardware-private fields, simulator-private fields, ABI-visible constants, test-only fields, or debug-only fields must be validated against SPEC_IR and GPU_STATE_IR.
---

# GPGPU Config Binding Validator

## Skill Role

This skill is the config ownership and binding validation pass.

```text
SPEC_IR.config_defaults + GPU_STATE_IR + CONFIG_BINDING_IR -> config_report
```

It validates config. It does not generate architecture defaults.

## Input IR

Required inputs:

- `SPEC_IR.config_defaults`
- `GPU_STATE_IR`
- `CONFIG_BINDING_IR`
- runtime contract when ABI fields are present

## Output IR

Emit:

```text
config_report = {
  config_hash,
  hardware_private,
  simulator_private,
  hw_sw_abi,
  test_only,
  debug_only,
  binding_results,
  ownership_violations,
  verdict
}
```

## Allowed Transformations

- Classify config fields into ownership classes.
- Check each config field binds to one `SPEC_IR` or `GPU_STATE_IR` field.
- Check generated artifacts cite state hash and transform table version.
- Check ABI-visible constants appear in runtime contract.

## Forbidden Actions

- Do not generate missing defaults.
- Do not treat generated config as source of truth.
- Do not let runtime modify `hardware_private` fields.
- Do not let `simulator_private` fields affect RTL trace.
- Do not let `test_only` or `debug_only` fields affect canonical execution semantics.

## Required Invariants

- `hw_sw_abi` fields are present in runtime contract.
- `hardware_private` fields are not runtime-controlled.
- `simulator_private` fields do not alter hardware semantics.
- `test_only` and `debug_only` fields are excluded from `GPU_STATE_IR` execution semantics.
- Every config enum is resolved by `gpgpu-spec-lock`.

## Failure Modes

Reject when:

- an ABI-visible constant exists only in RTL
- a config field has multiple owners
- a debug/test field affects execution state
- simulator-only config changes RTL trace
- a default is not traceable to `SPEC_IR`

## Report Schema

`config_report.verdict = CONFIG_LOCKED | CONFIG_REJECTED`.

## Downstream Contract

Runtime, RTL, simulator, and tests must consume only their declared config class. Closure uses `config_report` as evidence for the config lock gate.
