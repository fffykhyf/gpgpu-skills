# DESIGN_INTENT_IR v1

## Role

`DESIGN_INTENT_IR` locks a from-zero GPGPU design goal before any architecture synthesis happens.

It captures what the user wants, what is out of scope, the target workload, the target platform, and validation targets. It is not an architecture description.

## Schema

```text
DESIGN_INTENT_IR = {
  schema_version,
  intent_id,
  objective,
  non_goals,
  workload_profile,
  target_platform,
  hard_constraints,
  soft_constraints,
  required_features,
  optional_features,
  validation_target,
  prototype_credibility_target,
  preset,
  source_request_hash,
  locked_by
}
```

## Required Fields

| Field | Requirement |
|---|---|
| `schema_version` | Must be `DESIGN_INTENT_IR.v1`. |
| `intent_id` | Stable identifier derived from input hash. |
| `objective` | One explicit design objective. |
| `non_goals` | Explicit exclusions; empty list is allowed only when stated. |
| `workload_profile` | Workload class, compute/memory tendency, and required kernels. |
| `target_platform` | ASIC, FPGA, simulator, or teaching target with resource context. |
| `hard_constraints` | Non-negotiable constraints. |
| `soft_constraints` | Preference constraints that may be traded off. |
| `required_features` | Features that must be mapped by the synthesizer. |
| `optional_features` | Features that may be omitted with justification. |
| `validation_target` | Minimum validation level required for acceptance. |
| `prototype_credibility_target` | Required credibility level such as `TRACE_ONLY`, `RTL_SIMULATION`, or `SYNTHESIS_REPORT`. |
| `preset` | Explicit preset enum or `NONE_EXPLICIT`. |
| `source_request_hash` | Hash of the locked user request. |
| `locked_by` | Must be `gpgpu-design-intent-lock`. |

## Allowed Presets

```text
MINIMAL_TEACHING_GPGPU
RESEARCH_SIMT_BASELINE
FPGA_SMALL_GPGPU
RTL_SYNTHESIZABLE_BASELINE
GPGPU_WITH_TENSOR_EXTENSION
NONE_EXPLICIT
```

## Forbidden Fields

`DESIGN_INTENT_IR` must not contain architecture choices:

```text
warp_size
sm_count
cache_size
cache_policy
scheduler_policy
ISA_encoding
RTL_pipeline
register_file_capacity
shared_memory_capacity
```

## Verification Rules

- Objective, workload profile, target platform, and validation target must be present.
- Every preset must be from the allowed enum list.
- No natural-language ambiguity may be passed through as an architecture value.
- Missing architecture values must remain missing; do not fill defaults here.

