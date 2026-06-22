# Minimal Complete Spec

## input_kind

`COMPLETE_SPEC`

## expected_path

```text
gpgpu-mode-controller
 -> gpgpu-spec-lock
 -> gpgpu-canonical-state-engine
 -> gpgpu-deterministic-transform-engine
 -> validators
```

## expected_result

`PASS`

## expected_reason

All required `SPEC_IR` fields are present, explicit, and provenance-bearing.

