# GPGPU Design Flow

This flow is a self-correcting GPGPU design system. Skills are modules. Schemas define accepted IR. Tables define decisions. Examples and tests define regression behavior.

## Active Flow

```text
Architecture Generator
  -> System Contract + Golden Semantics Engine
  -> Incremental RTL Binding Engine
  -> Simulation + Performance Attribution Engine
  -> Architecture Rewrite Loop Controller
  -> back to Architecture Generator / Contract / RTL Binding
```

## Module 1: Architecture Generator

Input: user intent, optional spec, optional trace, patch request, presets, constraints, and reference evidence.

Output:

- `DESIGN_INTENT_IR`
- `ARCH_IR`
- `MICRO_CONSTRAINT_ESTIMATE_IR`

This module estimates area, memory pressure, warp occupancy, register pressure, shared-memory pressure, bandwidth need, and unrealizable risks before contract freeze.

## Module 2: System Contract + Golden Semantics Engine

Input: `ARCH_IR` and micro-constraint estimates.

Output:

- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `CONTRACT_SEMANTICS_REPORT`

`SYSTEM_CONTRACT_IR` is the only semantic truth source. `GOLDEN_CONTRACT_MODEL` is executable reference semantics derived from it, not a second simulator or second ISA source.

## Module 3: Incremental RTL Binding Engine

Input: `SYSTEM_CONTRACT_IR`, `GOLDEN_CONTRACT_MODEL`, module catalog, and interface tables.

Output:

- `INCREMENTAL_RTL_MAP`
- `MODULE_INTERFACE_REPORT`
- `RTL_PARTIAL_SIM_REPORT`

RTL is assembled module by module. Each module declares consumed contract paths, provided signals, required signals, latency contract, local trace schema, and partial simulation evidence.

## Module 4: Simulation + Performance Attribution Engine

Input: runtime, memory, RTL, waveform-derived, module partial-sim, and golden contract traces.

Output:

- `NORMALIZED_TRACE_IR`
- `PERF_ATTRIBUTION_GRAPH`
- `ROOT_CAUSE_REPORT`

The attribution graph must connect cycle, warp, memory, contract path, and RTL module evidence. A performance conclusion without that causal chain is insufficient evidence.

## Module 5: Architecture Rewrite Loop Controller

Input: `PERF_ATTRIBUTION_GRAPH`, `ROOT_CAUSE_REPORT`, `ARCH_IR`, `SYSTEM_CONTRACT_IR`, `GOLDEN_CONTRACT_MODEL`, `INCREMENTAL_RTL_MAP`, and regression history.

Output:

- `ARCH_REWRITE_PLAN`
- `REWRITE_DECISION_REPORT`
- `REGRESSION_TRACKING_REPORT`

The controller may propose Architecture Patch, Contract Patch, RTL Patch, or Test Evidence Patch. It must not directly mutate IR. Every patch routes to the owning module and triggers revalidation.

## Legacy Migration Path

Legacy v4 top-level skills and the old `legacy/` skill archive are not active wrappers. They were deleted after their useful constraints were migrated into the current owner modules and core constraint files:

- `gpgpu-front-end` and `gpgpu-architecture-synthesizer` constraints live in `gpgpu-architecture-generator/legacy_request_and_candidate_constraints.md`.
- `gpgpu-spec-lock` and `gpgpu-canonical-state-engine` constraints live in `gpgpu-system-contract-golden-engine/contract_truth_and_state_model.md`.
- `gpgpu-artifact-contract-engine`, structural memory-path, runtime interface, and implementation binding constraints live in `gpgpu-incremental-rtl-binding-engine/module_binding_rules.md`.
- `gpgpu-runtime-validator`, memory validation, and implementation trace constraints live in `gpgpu-simulation-performance-attribution-engine/legacy_validation_and_trace_constraints.md`.
- `gpgpu-closure-refinement-engine` constraints live in `gpgpu-architecture-rewrite-loop-controller/legacy_closure_repair_constraints.md`.

## Fail Closed Policy

Missing schema, missing table row, hidden default, unsupported enum, forbidden provenance, unmapped contract paths, interface mismatches, missing causal evidence, and unowned rewrite triggers must reject or emit `INSUFFICIENT_SKILL_ASSET`.
