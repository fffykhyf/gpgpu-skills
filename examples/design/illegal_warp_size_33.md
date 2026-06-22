# Illegal Warp Size 33

## input_kind

`DESIGN_INTENT`

## expected_path

```text
gpgpu-design-intent-lock
 -> gpgpu-architecture-synthesizer
```

## expected_result

`REJECT_BY_HARD_CONSTRAINT`

## expected_first_gate

`warp_mask_width_consistency`

## expected_reason

The requested warp size cannot satisfy the allowed enum table or active-mask width constraint for the selected template.

