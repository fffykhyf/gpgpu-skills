# Illegal Missing Warp Size

## input_kind

`COMPLETE_SPEC`

## expected_path

```text
gpgpu-mode-controller
 -> gpgpu-spec-lock
```

## expected_result

`REJECT_BY_SPEC_LOCK`

## expected_first_gate

`required_field_presence`

## expected_reason

`warp_model.width` is absent and cannot be inferred from common GPU defaults.

