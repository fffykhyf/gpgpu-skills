# Skill Summary: GPGPU Skills v5

`skill/` now defines a self-correcting GPGPU design system:

```text
Architecture Generator
  -> System Contract + Golden Semantics Engine
  -> Incremental RTL Binding Engine
  -> Simulation + Performance Attribution Engine
  -> Architecture Rewrite Loop Controller
  -> back to Architecture Generator / Contract / RTL Binding
```

## Top-Level Skills

| Skill | Responsibility |
|---|---|
| `gpgpu-architecture-generator` | Intent intake, candidate `ARCH_IR`, and `MICRO_CONSTRAINT_ESTIMATE_IR` |
| `gpgpu-system-contract-golden-engine` | `SYSTEM_CONTRACT_IR` and executable `GOLDEN_CONTRACT_MODEL` |
| `gpgpu-incremental-rtl-binding-engine` | Module-by-module `INCREMENTAL_RTL_MAP`, interfaces, and partial simulation |
| `gpgpu-simulation-performance-attribution-engine` | Trace normalization, `PERF_ATTRIBUTION_GRAPH`, and root cause evidence |
| `gpgpu-architecture-rewrite-loop-controller` | `ARCH_REWRITE_PLAN`, patch routing, and regression tracking |

## Legacy Migration Mapping

The old v4 top-level skills are no longer active. Their useful constraints were migrated into the v5 owner skills:

| Removed v4 skill | Migrated owner |
|---|---|
| `gpgpu-front-end` | `gpgpu-architecture-generator` |
| `gpgpu-architecture-synthesizer` | `gpgpu-architecture-generator` |
| `gpgpu-spec-lock` | `gpgpu-system-contract-golden-engine` |
| `gpgpu-canonical-state-engine` | `gpgpu-system-contract-golden-engine` |
| `gpgpu-artifact-contract-engine` | `gpgpu-system-contract-golden-engine` + `gpgpu-incremental-rtl-binding-engine` |
| `gpgpu-runtime-validator` | `gpgpu-system-contract-golden-engine` + `gpgpu-simulation-performance-attribution-engine` |
| `gpgpu-memory-subsystem` | `gpgpu-system-contract-golden-engine` + `gpgpu-incremental-rtl-binding-engine` + `gpgpu-simulation-performance-attribution-engine` |
| `gpgpu-implementation-validator` | `gpgpu-incremental-rtl-binding-engine` + `gpgpu-simulation-performance-attribution-engine` |
| `gpgpu-closure-refinement-engine` | `gpgpu-architecture-rewrite-loop-controller` |

## Core Rule

Contracts are executable, RTL binding is incremental, performance attribution is causal, and closure produces rewrite plans instead of only reports.

`shared/` is intentionally minimal: it keeps only v5 schemas, tables, tests, references, flow docs, and the `self_correcting_minimal_simt` example required by the current skills.
