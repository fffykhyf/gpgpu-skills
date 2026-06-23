---
name: gpgpu-loop
description: Use when PERF_ATTRIBUTION_GRAPH, ROOT_CAUSE_REPORT, PASS_EVIDENCE_REPORT, toolchain artifacts, INCREMENTAL_RTL_MAP, SYSTEM_CONTRACT_IR, GOLDEN_CONTRACT_MODEL, or ARCH_IR evidence must trigger architecture, contract, golden-model, toolchain, runtime, RTL, pass-evidence, or test-evidence rewrite plans and revalidation routing.
---

# GPGPU Architecture Rewrite Loop Controller

## Role

This skill is the self-correction controller. It reads attribution evidence and emits rewrite plans that route work back to the appropriate owner module.

## Position in Flow

Upstream:
- `gpgpu-arch`
- `gpgpu-golden`
- `gpgpu-runtime`
- `gpgpu-rtl`
- `gpgpu-simppa`

Downstream:
- `gpgpu-arch` for architecture patches
- `gpgpu-golden` for contract patches
- `gpgpu-golden` for golden-model patches
- `gpgpu-runtime` for toolchain and runtime patches
- `gpgpu-rtl` for RTL patches
- `gpgpu-simppa` for pass-evidence, test-evidence, and revalidation patches

## Input IR

Consumes:
- `ARCH_IR`
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `TOOLCHAIN_ARTIFACT_IR`
- `PROGRAM_IMAGE_IR`
- `RUNTIME_LAUNCH_IR`
- `LOADER_CONTRACT_IR`
- `INCREMENTAL_RTL_MAP`
- `PERF_ATTRIBUTION_GRAPH`
- `ROOT_CAUSE_REPORT`
- `PASS_EVIDENCE_REPORT`
- `REGRESSION_FINGERPRINT`
- regression history
- patch taxonomy
- rewrite trigger table

## Output IR

Produces:
- `ARCH_REWRITE_PLAN`
- `REWRITE_DECISION_REPORT`
- `REGRESSION_TRACKING_REPORT`

## Owned Decisions

This skill owns:
- rewrite trigger selection
- architecture patch planning
- contract patch planning
- golden-model patch planning
- toolchain patch planning
- runtime patch planning
- RTL patch planning
- pass evidence patch planning
- test evidence patch planning
- revalidation routing
- regression tracking

## Forbidden Actions

This skill must not:
- directly mutate `ARCH_IR`
- directly mutate `SYSTEM_CONTRACT_IR`
- directly mutate `GOLDEN_CONTRACT_MODEL`
- directly mutate `TOOLCHAIN_ARTIFACT_IR`
- directly mutate `PROGRAM_IMAGE_IR`
- directly mutate `RUNTIME_LAUNCH_IR`
- directly mutate `LOADER_CONTRACT_IR`
- directly mutate `INCREMENTAL_RTL_MAP`
- directly mutate traces
- define new truth or module interfaces

## Required Tables

This skill must use:
- `shared/tables/rewrite_trigger_table.yaml`
- `shared/tables/patch_taxonomy_table.yaml`
- `shared/tables/revalidation_routing_table.yaml`
- `shared/tables/root_cause_taxonomy.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/arch_rewrite_plan.schema.yaml`
- `shared/schemas/rewrite_decision_report_ir.schema.yaml`
- `shared/schemas/regression_tracking_report_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- `ARCH_REWRITE_PLAN` may propose architecture, contract, golden-model, toolchain, runtime, RTL, pass-evidence, or test-evidence patches, but must not directly mutate `ARCH_IR`, `SYSTEM_CONTRACT_IR`, `GOLDEN_CONTRACT_MODEL`, `TOOLCHAIN_ARTIFACT_IR`, `PROGRAM_IMAGE_IR`, `RUNTIME_LAUNCH_IR`, `LOADER_CONTRACT_IR`, `INCREMENTAL_RTL_MAP`, or traces.
- Every patch has owner module, patch target, expected impact, required revalidation gates, regression risks, and rejected alternatives.
- Architecture Patch, Contract Patch, Golden Model Patch, Toolchain Patch, Runtime Patch, RTL Patch, Pass Evidence Patch, and Test Evidence Patch are distinct patch classes.
- `RUNTIME_LAUNCH_ROOT_CAUSE` routes to `RUNTIME_PATCH`, not `TOOLCHAIN_PATCH`.
- `PERFORMANCE_ARCH_ROOT_CAUSE` may trigger `ARCHITECTURE_PATCH` only with performance metric refs, causal graph refs, contract paths, RTL module paths, bottleneck cycle window, counter evidence, and rejected RTL/contract/runtime alternatives.
- `PASS_EVIDENCE_PATCH` remains valid for incomplete pass evidence, unstable fingerprints, missing coverage, or insufficient trace collection.
- Every accepted rewrite routes to revalidation.

## Failure Modes

This skill must emit:
- `UNSUPPORTED_REWRITE_TRIGGER`
- `PATCH_OWNER_MISSING`
- `TOOLCHAIN_PATCH_OWNER_MISSING`
- `RUNTIME_PATCH_OWNER_MISSING`
- `PASS_EVIDENCE_PATCH_OWNER_MISSING`
- `REVALIDATION_ROUTE_MISSING`
- `REGRESSION_RISK_UNBOUNDED`
- `INSUFFICIENT_TRACE_EVIDENCE`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- verdict
- rewrite_id
- trigger_root_cause
- trigger_root_cause_subclass
- patch_type
- patch_targets
- owner_module
- expected_impact
- required_revalidation_gates
- regression_risks
- rejected_alternatives
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `rewrite_trigger.md`
- `patch_taxonomy.md`
- `regression_tracking.md`
- `revalidation_routing.md`
- `legacy_closure_repair_constraints.md`
- `shared/schemas/arch_rewrite_plan.schema.yaml`
- `shared/schemas/rewrite_decision_report_ir.schema.yaml`
- `shared/schemas/regression_tracking_report_ir.schema.yaml`
- `shared/tables/rewrite_trigger_table.yaml`
- `shared/tables/patch_taxonomy_table.yaml`
- `shared/tables/revalidation_routing_table.yaml`
- `shared/tests/architecture_rewrite_loop_controller/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_arch_rewrite_plan.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
