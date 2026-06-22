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

## Fail Closed Policy

Missing schema, missing table row, hidden default, unsupported enum, forbidden provenance, and unmapped state fields must reject or emit `INSUFFICIENT_SKILL_ASSET`. They must not be repaired by model inference.
