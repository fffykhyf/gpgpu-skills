---
name: gpgpu-synthesis-closure-engine
description: Use when a GPGPU architecture candidate, SPEC_IR, GPU_STATE_IR, artifacts, and validation reports must be accepted, rejected, refined, or marked insufficient.
---

# GPGPU Synthesis Closure Engine

## Skill Role

This skill is the DESIGN-mode acceptance pass.

```text
ARCH_CANDIDATE_IR + SPEC_IR + GPU_STATE_IR + validation reports
  -> SYNTHESIS_ACCEPTANCE_REPORT_IR
```

It does not design architecture. It prevents bad candidates from passing.

## Input IR

Required inputs:

- `ARCH_CANDIDATE_IR`
- `SPEC_IR`
- `GPU_STATE_IR`
- transform artifact coverage report
- config report
- runtime launch smoke report
- memory ordering smoke report
- RTL implementability report
- golden trace report
- optional causal refinement evidence

## Output IR

Emit:

```text
SYNTHESIS_ACCEPTANCE_REPORT_IR = {
  candidate_id,
  input_hash,
  spec_ir_hash,
  gpu_state_hash,
  hard_constraint_result,
  requirement_coverage_result,
  spec_round_trip_result,
  state_invariant_result,
  artifact_mapping_result,
  config_lock_result,
  trace_smoke_result,
  quality_gate_result,
  stability_result,
  verdict,
  repair_request
}
```

## Allowed Transformations

- Aggregate gate results.
- Compare candidate identity, spec hash, and state hash.
- Convert failed gates into `repair_request` data.
- Route repairable failures back to `gpgpu-architecture-synthesizer`.

## Forbidden Actions

- Do not modify `ARCH_CANDIDATE_IR`.
- Do not modify `SPEC_IR`.
- Do not modify `GPU_STATE_IR`.
- Do not accept missing evidence as pass.
- Do not design a replacement architecture.

## Required Invariants

The closure report must evaluate:

1. Requirement coverage.
2. Spec round trip.
3. State invariants.
4. Artifact mapping.
5. Config lock.
6. Trace smoke.
7. Quality gate.
8. Stability gate.

v2 minimum may enforce the first four gates and mark the rest as `INSUFFICIENT_EVIDENCE`.

## Failure Modes

- `REJECT` for hard correctness failure.
- `REFINE_REQUIRED` for repairable trace or quality failure.
- `INSUFFICIENT_EVIDENCE` for missing evidence.
- `ACCEPT` only when all required gates pass.

## Report Schema

`verdict` is restricted to:

```text
ACCEPT
REJECT
REFINE_REQUIRED
INSUFFICIENT_EVIDENCE
```

`repair_request` must include failed gate, affected state field when known, and evidence trace when available.

## Downstream Contract

Only an `ACCEPT` report may be used as final DESIGN-mode acceptance. `REFINE_REQUIRED` must route through:

```text
gpgpu-synthesis-closure-engine -> gpgpu-architecture-synthesizer
```
