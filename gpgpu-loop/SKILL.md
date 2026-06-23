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
- `gpgpu-interconnect` for NoC/fabric patches
- `gpgpu-memory` for DRAM/coherence patches
- `gpgpu-atomic-sync` for atomic/barrier/fence patches
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
- `shared/references/vortex_memory_sync_lessons.yaml`

## Output IR

Produces:
- `ARCH_REWRITE_PLAN`
- `REWRITE_DECISION_REPORT`
- `REGRESSION_TRACKING_REPORT`
- `REWRITE_TRIGGER_REPORT`
- `COUNTER_REGRESSION_REPORT`
- `ATTRIBUTION_VALIDITY_REPORT`
- `PATCH_ROUTING_DECISION`
- `CONFIG_DRIFT_REPORT`

Human-facing reports:
- `PATCH_CARD.zh.md`
- `REGRESSION_SUMMARY.zh.md`

AI-facing artifacts:
- English `ARCH_REWRITE_PLAN.yaml`
- English `REWRITE_DECISION_REPORT.yaml`
- English `REGRESSION_TRACKING_REPORT.yaml`
- English `REWRITE_TRIGGER_REPORT.md`
- English `COUNTER_REGRESSION_REPORT.md`
- English `ATTRIBUTION_VALIDITY_REPORT.md`
- English `PATCH_ROUTING_DECISION.md`
- English `CONFIG_DRIFT_REPORT.md`

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
- interconnect patch planning
- memory-system patch planning
- atomic/synchronization patch planning
- advanced memory-path and synchronization migration-risk routing
- revalidation routing
- regression tracking
- counter-gated regression selection
- attribution-driven rewrite trigger selection
- patch routing by queue/stage owner
- config drift guard
- simulator artifact guard

Required reference lessons:
- `VORTEX_SIMX_RTL_TWIN`

## Human and AI Output Policy

`ARCH_REWRITE_PLAN`, `REWRITE_DECISION_REPORT`, and
`REGRESSION_TRACKING_REPORT` are AI-facing English artifacts. Human-facing output
must be `PATCH_CARD.zh.md`, written in Chinese and limited to issue summary,
evidence summary, selected patch type, owner module, required revalidation, and
regression risks.

When a regression reappears or the same patch repeats, also emit
`REGRESSION_SUMMARY.zh.md`. Do not expose the full rewrite YAML by default unless
the user asks, root cause is ambiguous, or the target owner needs exact patch
fields. Full English rewrite, decision, and regression artifacts must be
registered in `ARTIFACT_MANIFEST_IR`.

## Counter-Gated Regression

Functional correctness does not pass the loop when counters regress. Trigger
rewrite for unexpected coalesced transaction growth, unexplained scoreboard wait,
barrier/membar/atomic waits without contracts, cache reservation fail spikes,
ICNT `has_buffer` failure spikes, L2 queue full misattributed as DRAM, missing
counter producers, or simulator-private parameters entering hardware contracts.

## Attribution-Driven Rewrite Trigger

Trigger rewrite when a performance conclusion lacks symptom counter, exclusion
counter, queue/stage owner, fix target, confidence, or producer-backed evidence.
Power-only bottleneck claims are attribution failures.

## Patch Routing Rule

Route by owning contract: architecture, contract/golden, RTL, memory,
interconnect, atomic sync, runtime ABI, counter schema, test evidence, or
simulator artifact removal. Do not route by symptom wording alone.

## Config Drift Guard

Reject rewrite plans that let simulator-private parameters, CUDA/PTX compatibility
fields, fixed latencies, tested-config queue depths, BookSim knobs, or
AccelWattch coefficients enter native hardware/ABI contracts.

## Simulator-Artifact Guard

If a patch introduces C++ queues, BookSim config, AccelWattch internals, CUDA
stream stack, fixed simulator latency, PTX opcode latency, or parser-only
counters into design truth, route to `SIMULATOR_ARTIFACT_REMOVAL_PATCH`.

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
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/tables/human_report_template_table.yaml`
- `shared/tables/rewrite_trigger_table.yaml`
- `shared/tables/patch_taxonomy_table.yaml`
- `shared/tables/revalidation_routing_table.yaml`
- `shared/tables/root_cause_taxonomy.yaml`
- `shared/tables/gpgpusim_config_taxonomy_seed.md`
- `shared/tables/stall_reason_taxonomy.md`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/arch_rewrite_plan.schema.yaml`
- `shared/schemas/rewrite_decision_report_ir.schema.yaml`
- `shared/schemas/regression_tracking_report_ir.schema.yaml`
- `shared/schemas/counter_manifest.schema.yaml`
- `shared/schemas/stall_reason_matrix.schema.yaml`
- `shared/schemas/performance_attribution_graph.schema.yaml`
- `shared/schemas/config_parameter_classification.schema.yaml`

## Required Invariants

The output must satisfy:
- `ARCH_REWRITE_PLAN` may propose architecture, contract, golden-model, toolchain, runtime, RTL, pass-evidence, or test-evidence patches, but must not directly mutate `ARCH_IR`, `SYSTEM_CONTRACT_IR`, `GOLDEN_CONTRACT_MODEL`, `TOOLCHAIN_ARTIFACT_IR`, `PROGRAM_IMAGE_IR`, `RUNTIME_LAUNCH_IR`, `LOADER_CONTRACT_IR`, `INCREMENTAL_RTL_MAP`, or traces.
- Every patch has owner module, patch target, expected impact, required revalidation gates, regression risks, and rejected alternatives.
- Architecture Patch, Contract Patch, Golden Model Patch, Toolchain Patch, Runtime Patch, RTL Patch, Interconnect Patch, Memory Patch, Atomic Sync Patch, Pass Evidence Patch, and Test Evidence Patch are distinct patch classes.
- Advanced memory-path and synchronization rewrites must route SM hierarchy, warp state, memory bundle, NoC, DRAM, coherence, atomic, barrier, fence, and WSYNC changes to their owning skill.
- `RUNTIME_LAUNCH_ROOT_CAUSE` routes to `RUNTIME_PATCH`, not `TOOLCHAIN_PATCH`.
- `PERFORMANCE_ARCH_ROOT_CAUSE` may trigger `ARCHITECTURE_PATCH` only with performance metric refs, causal graph refs, contract paths, RTL module paths, bottleneck cycle window, counter evidence, and rejected RTL/contract/runtime alternatives.
- `PASS_EVIDENCE_PATCH` remains valid for incomplete pass evidence, unstable fingerprints, missing coverage, or insufficient trace collection.
- Counter regressions can trigger rewrite even when final architectural state and memory dumps match golden.
- Patch classes include `MEMORY_PATCH`, `INTERCONNECT_PATCH`, `ATOMIC_SYNC_PATCH`, `RUNTIME_ABI_PATCH`, `COUNTER_SCHEMA_PATCH`, and `SIMULATOR_ARTIFACT_REMOVAL_PATCH` in addition to existing architecture, contract, RTL, and test-evidence patch classes.
- Root-cause routing must preserve queue/stage owner and producer-audit status.
- Simulator-private parameter drift must route to config or simulator-artifact removal, not silently pass.
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
- `counter_gated_regression.md`
- `attribution_driven_rewrite_trigger.md`
- `patch_routing_rule.md`
- `config_drift_guard.md`
- `simulator_artifact_guard.md`
- `shared/schemas/arch_rewrite_plan.schema.yaml`
- `shared/schemas/rewrite_decision_report_ir.schema.yaml`
- `shared/schemas/regression_tracking_report_ir.schema.yaml`
- `shared/schemas/counter_manifest.schema.yaml`
- `shared/schemas/performance_attribution_graph.schema.yaml`
- `shared/templates/rewrite_trigger_report.md`
- `shared/tables/rewrite_trigger_table.yaml`
- `shared/tables/patch_taxonomy_table.yaml`
- `shared/tables/revalidation_routing_table.yaml`
- `shared/tests/architecture_rewrite_loop_controller/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_arch_rewrite_plan.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
