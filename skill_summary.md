# Skill Summary: GPGPU Skills v4

`skill/` now defines a 9-pass GPGPU design compiler flow:

```text
User Request / Spec
  -> Front-End
  -> Architecture Candidate
  -> Spec Lock
  -> Canonical State
  -> Artifact Contract
  -> Runtime / Memory / Implementation Validation
  -> Closure / Refinement
```

## Top-Level Skills

| Skill | Responsibility |
|---|---|
| `gpgpu-front-end` | mode selection and design intent lock |
| `gpgpu-architecture-synthesizer` | DESIGN_INTENT_IR to ARCH_CANDIDATE_IR and SYNTHESIZED_SPEC_DRAFT |
| `gpgpu-spec-lock` | complete spec or draft to stable SPEC_IR |
| `gpgpu-canonical-state-engine` | SPEC_IR to GPU_STATE_IR |
| `gpgpu-artifact-contract-engine` | deterministic artifact mapping and config binding |
| `gpgpu-runtime-validator` | host/runtime/launch ABI validation |
| `gpgpu-memory-subsystem` | memory subsystem and RTL-facing memory path validation |
| `gpgpu-implementation-validator` | RTL and golden sim validation plus first divergence |
| `gpgpu-closure-refinement-engine` | acceptance, failure attribution, and refinement request generation |

## Legacy Mapping

| v4 skill | v3 source |
|---|---|
| `gpgpu-front-end` | `gpgpu-mode-controller` + `gpgpu-design-intent-lock` |
| `gpgpu-architecture-synthesizer` | retained |
| `gpgpu-spec-lock` | retained |
| `gpgpu-canonical-state-engine` | retained |
| `gpgpu-artifact-contract-engine` | `gpgpu-deterministic-transform-engine` + `gpgpu-config` |
| `gpgpu-runtime-validator` | `gpgpu-runtime` |
| `gpgpu-memory-subsystem` | `gpgpu-memory-path` |
| `gpgpu-implementation-validator` | `gpgpu-rtl-simt-core` + `gpgpu-golden-sim` |
| `gpgpu-closure-refinement-engine` | `gpgpu-synthesis-closure-engine` + `gpgpu-causal-trace-analyzer` |

## Shared Assets

`shared/schemas/` defines IR contracts. `shared/tables/` defines decisions and mappings. `shared/examples/` contains end-to-end expected outputs. `shared/tests/` contains per-skill regression cases plus `validate_v4_assets.py`. `shared/references/` converts project references into lesson/rule/evidence entries.

## Fail-Closed Principle

Missing schema, missing table rows, hidden defaults, unknown enums, forbidden provenance, and unmapped state fields must emit a reject verdict or `INSUFFICIENT_SKILL_ASSET`. The flow must not fill gaps with model guesses.
