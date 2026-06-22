# Memory Bandwidth Insufficient

## input_kind

`DESIGN_INTENT`

## expected_path

```text
gpgpu-design-intent-lock
 -> gpgpu-architecture-synthesizer
 -> gpgpu-synthesis-closure-engine
 -> gpgpu-causal-trace-analyzer
```

## expected_result

`REFINE_REQUIRED_BY_QUALITY_GATE`

## expected_reason

The candidate can be structurally valid but fail memory bandwidth quality targets, producing a refinement request instead of acceptance.

