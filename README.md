# GPGPU Skills

This repository now defines a self-correcting GPGPU design system.

## Goals

1. Generate candidate GPGPU architectures from intent and constraints.
2. Freeze one system contract and derive executable golden semantics.
3. Build RTL incrementally module by module with interface checks.
4. Normalize execution traces and build causal performance attribution.
5. Produce architecture, contract, RTL, or test-evidence rewrite plans.

## Current Top-Level Skills

1. `gpgpu-architecture-generator`
2. `gpgpu-system-contract-golden-engine`
3. `gpgpu-incremental-rtl-binding-engine`
4. `gpgpu-simulation-performance-attribution-engine`
5. `gpgpu-architecture-rewrite-loop-controller`

## Flow

```text
Architecture Generator
  -> System Contract + Golden Semantics Engine
  -> Incremental RTL Binding Engine
  -> Simulation + Performance Attribution Engine
  -> Architecture Rewrite Loop Controller
  -> back to Architecture Generator / Contract / RTL Binding
```

## Core Outputs

- `ARCH_IR`
- `MICRO_CONSTRAINT_ESTIMATE_IR`
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `INCREMENTAL_RTL_MAP`
- `PERF_ATTRIBUTION_GRAPH`
- `ARCH_REWRITE_PLAN`

## Legacy Migration

The former 9-stage top-level GPGPU skills and the old `legacy/` skill archive have been deleted from the active skill namespace. Their useful constraints were migrated into the current owner skills as `legacy_*_constraints.md` references. New work must use the five current top-level skills; old truth, validation, memory, RTL, and closure behavior must not reappear as separate top-level skills.

## Shared Assets

Only v5 assets are retained under `shared/`; old top-level examples, old IR references, v4-only schemas, v4-only tables, and v4 test/example directories are deleted and guarded by the validator.

- `shared/schemas/` defines IR and report contracts.
- `shared/tables/` defines deterministic decision tables.
- `shared/examples/self_correcting_minimal_simt/` demonstrates the closed loop.
- `shared/tests/` contains regression cases and the asset validator.
- `shared/flow/` describes the active design flow.

## Fail-Closed Principle

Missing schema, missing table row, hidden default, unsupported enum, forbidden provenance, unmapped contract path, interface mismatch, missing causal evidence, and unowned rewrite triggers must reject or emit `INSUFFICIENT_SKILL_ASSET`. The flow must not fill gaps with model guesses.
