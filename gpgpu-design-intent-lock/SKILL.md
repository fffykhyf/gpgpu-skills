---
name: gpgpu-design-intent-lock
description: Use when a GPGPU request is a design goal rather than a complete architecture spec, especially from-zero design intents, presets, workloads, platforms, constraints, or validation targets.
---

# GPGPU Design Intent Lock

## Skill Role

This skill is the DESIGN-mode input stabilizer pass.

```text
natural-language design goal -> DESIGN_INTENT_IR
```

It locks user intent. It does not design architecture.

## Input IR

Input is a natural-language design goal plus optional explicit preset.

Required source facts:

- objective
- workload profile
- target platform
- validation target
- hard constraints or explicit `NONE`

## Output IR

Emit:

```text
DESIGN_INTENT_IR = {
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
  source_request_hash
}
```

## Allowed Transformations

- Normalize the user objective into one explicit objective field.
- Extract workload, platform, constraints, and validation targets.
- Convert a named preset into an allowed preset enum.
- Mark missing optional features as absent without filling architecture values.

Allowed presets:

```text
MINIMAL_TEACHING_GPGPU
RESEARCH_SIMT_BASELINE
FPGA_SMALL_GPGPU
RTL_SYNTHESIZABLE_BASELINE
GPGPU_WITH_TENSOR_EXTENSION
NONE_EXPLICIT
```

## Forbidden Actions

- Do not emit `SPEC_IR`.
- Do not choose SM count, warp size, cache policy, scheduler, ISA, memory hierarchy, register file size, or RTL pipeline.
- Do not infer architecture from examples.
- Do not pass unresolved natural language to `gpgpu-architecture-synthesizer`.

## Required Invariants

- Objective, workload profile, target platform, and validation target are explicit.
- Every preset is from the allowed enum table.
- Every non-goal remains a negative requirement and cannot be converted into a feature.
- No architecture field appears in `DESIGN_INTENT_IR`.

## Failure Modes

Reject when:

- objective is missing
- workload profile is missing
- target platform is missing
- validation target is missing
- preset is not one of the allowed enums
- the user request asks for architecture values without enough constraints to lock intent

## Report Schema

```text
DESIGN_INTENT_LOCK_REPORT = {
  input_hash,
  locked_fields,
  missing_required_fields,
  rejected_architecture_fields,
  selected_preset,
  verdict
}
```

`verdict = LOCKED | REJECTED | NEEDS_EXPLICIT_PRESET`.

## Downstream Contract

`gpgpu-architecture-synthesizer` may consume only the locked fields in `DESIGN_INTENT_IR`. It may not inspect the original natural-language request for extra architecture facts.
