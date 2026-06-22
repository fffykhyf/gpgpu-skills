---
name: gpgpu-architecture-synthesizer
description: Use when DESIGN_INTENT_IR must be converted into a bounded GPGPU architecture candidate using fixed templates, constraint tables, enum tables, and provenance.
---

# GPGPU Architecture Synthesizer

## Skill Role

This skill is the constrained DESIGN-mode synthesis pass.

```text
DESIGN_INTENT_IR -> ARCH_CANDIDATE_IR + synthesized_spec_draft
```

It creates candidates only. It does not create final truth.

## Input IR

Required inputs:

- `DESIGN_INTENT_IR`
- architecture preset library
- hard constraint table
- quality target table
- enum table

## Output IR

Emit:

```text
ARCH_CANDIDATE_IR = {
  candidate_id,
  ARCH_IR,
  synthesized_spec_draft,
  constraint_proof,
  requirement_coverage_matrix,
  quality_estimate,
  rejected_alternatives,
  unresolved_risks
}
```

## Allowed Transformations

### Stage 1: Requirement Coverage

Map each design requirement to an architecture owner or explicit non-goal.

### Stage 2: Template Selection

Select only from fixed templates:

```text
MINIMAL_SIMT_CORE
MULTI_WARP_SINGLE_SM
MULTI_SM_GPGPU
FPGA_SMALL_GPGPU
TENSOR_EXTENDED_GPGPU
```

v2 minimum implementation may support only:

```text
MINIMAL_SIMT_CORE
MULTI_WARP_SINGLE_SM
```

### Stage 3: Parameter Allocation

Allocate fields such as warp size, max warps per SM, register file size, shared memory size, issue width, scheduler count, LSU depth, and cache policy.

Every parameter must cite:

```text
USER_CONSTRAINT
DESIGN_PRESET
SOLVER_DERIVED
REPAIR_DERIVED
```

### Stage 4: Hard Constraint Checking

Check hard constraints before quality scoring.

### Stage 5: Quality Scoring

Emit risk estimates only after hard constraints pass.

## Forbidden Actions

- Do not output `GPU_STATE_IR`.
- Do not bypass `gpgpu-spec-lock`.
- Do not invent topology outside the template library.
- Do not use `COMMON_GPU_DEFAULT`, `MODEL_GUESS`, or `UNKNOWN` provenance.
- Do not continue to quality scoring after hard constraint failure.

## Required Invariants

- Every intent requirement has an owner or explicit non-goal.
- `warp_size == active_mask_width` is satisfied or rejected.
- `issue_width <= execution_unit_ports`.
- Memory request width does not exceed memory interface width.
- ISA operation classes have execution-unit owners.
- ABI-visible constants appear in `config_contract.hw_sw_abi`.

## Failure Modes

Emit `REJECTED_ARCH_CANDIDATE` when:

- a required feature has no owner
- template cannot support a hard requirement
- hard constraints fail
- any parameter lacks allowed provenance
- synthesized draft cannot be made complete without inference

## Report Schema

```text
ARCH_SYNTHESIS_REPORT = {
  candidate_id,
  selected_template,
  requirement_coverage_matrix,
  constraint_proof,
  rejected_alternatives,
  quality_estimate,
  unresolved_risks,
  verdict
}
```

`verdict = CANDIDATE_EMITTED | REJECTED_ARCH_CANDIDATE`.

## Downstream Contract

Downstream must treat `ARCH_CANDIDATE_IR` as candidate evidence only. The next truth-forming pass is:

```text
synthesized_spec_draft -> gpgpu-spec-lock -> SPEC_IR
```
