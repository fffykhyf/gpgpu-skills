# FPGA Small GPGPU Intent

## input_kind

`DESIGN_INTENT`

## expected_path

```text
gpgpu-mode-controller
 -> gpgpu-design-intent-lock
 -> gpgpu-architecture-synthesizer
 -> gpgpu-synthesis-closure-engine
```

## expected_result

`REFINE_REQUIRED_BY_QUALITY_GATE`

## expected_reason

The FPGA target may need resource evidence before acceptance if the prototype credibility target is `SYNTHESIS_REPORT`.

