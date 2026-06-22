# GPGPU Design Flow

This flow is an IR-centered compiler pipeline. Skills are passes. Schemas define accepted IR. Tables define decisions. Examples and tests define regression behavior.

## Reproduce Path

Input: complete `spec.md`.

```text
gpgpu-front-end
  -> MODE_SELECTION_IR: REPRODUCE
gpgpu-spec-lock
  -> SPEC_IR
gpgpu-canonical-state-engine
  -> GPU_STATE_IR
gpgpu-artifact-contract-engine
  -> RTL_MAPPING_IR / SIM_BEHAVIOR_IR / RUNTIME_CONTRACT_IR / MEMORY_MODEL_IR / CONFIG_BINDING_IR / VALIDATION_PLAN_IR
gpgpu-runtime-validator
gpgpu-memory-subsystem
gpgpu-implementation-validator
  -> validation reports
gpgpu-closure-refinement-engine
  -> ACCEPT / REJECT / REFINE_REQUIRED / INSUFFICIENT_EVIDENCE
```

Stability requirement: the same input spec must produce the same SPEC_IR hash, GPU_STATE_IR hash, artifact mapping report, and closure verdict.

## Design From Intent Path

Input: design goal.

```text
gpgpu-front-end
  -> MODE_SELECTION_IR: DESIGN
  -> DESIGN_INTENT_IR
gpgpu-architecture-synthesizer
  -> ARCH_CANDIDATE_IR
  -> SYNTHESIZED_SPEC_DRAFT
gpgpu-spec-lock
  -> SPEC_IR
```

After SPEC_IR, the path rejoins the reproduce path. The synthesizer must not skip spec-lock.

## Vertical Slice Prototype Path

Input: a request to run a minimal GPU demo end to end.

```text
CUDA-like Python kernel
  -> frontend_subset_contract
  -> assembler_contract
  -> program.hex / PROGRAM_IMAGE_CONTRACT_IR
  -> RTL sim smoke
  -> memory dump
  -> golden_output_contract
  -> closure
```

This path uses `MINIMAL_VERTICAL_SLICE_GPGPU`, `software_stack_contract_table.yaml`, `end_to_end_smoke_test_table.yaml`, and `vertical_slice_validation_table.yaml`. It must still pass `SPEC_IR -> GPU_STATE_IR -> artifact contract -> validation closure`; the runnable demo is evidence, not a second source of truth.

## Fail Closed Policy

Missing schema, missing table row, hidden default, unsupported enum, forbidden provenance, and unmapped state fields must reject or emit `INSUFFICIENT_SKILL_ASSET`. They must not be repaired by model inference.
