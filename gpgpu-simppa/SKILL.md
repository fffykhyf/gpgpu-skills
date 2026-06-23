---
name: gpgpu-simppa
description: Use when RTL simulation, golden execution, runtime, memory, module, waveform, or toolchain traces must be normalized into correctness evidence, performance metrics, causal attribution, pass evidence, regression fingerprints, and rewrite routing reports.
---

# GPGPU Simulation Evidence and Performance Attribution Engine

## Role

This skill consumes contract, golden, RTL, runtime, memory, module, waveform,
and toolchain traces. It normalizes evidence, decides whether the run is a
correctness failure or a correctness pass, performs failure attribution only
when required, extracts performance metrics, records pass evidence, and emits
reports for rewrite routing or regression tracking.

When RTL and golden outputs match, this skill must not skip execution. A match
only disables failure localization unless trace-level architectural divergence
exists. The skill still produces pass evidence, coverage summary, performance
metrics, and a regression fingerprint.

## Position in Flow

Upstream:
- `gpgpu-golden`
- `gpgpu-runtime`
- `gpgpu-rtl`

Downstream:
- `gpgpu-loop`

Flow:

```text
RTL simulation + golden execution + toolchain/runtime evidence
  -> Trace Ingestion + Normalization
  -> Correctness Gate
  -> Failure Attribution Mode or Pass Evidence Mode
  -> Performance Metric Extraction
  -> Causal Graph when required
  -> Root Cause / No Root Cause
  -> Rewrite Handoff / Regression Fingerprint
  -> SIM_PERF_ATTRIBUTION_REPORT
```

## Input IR

Consumes:
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `INCREMENTAL_RTL_MAP`
- `TOOLCHAIN_ARTIFACT_IR`
- `PROGRAM_IMAGE_IR`
- `RUNTIME_LAUNCH_IR`
- `LOADER_CONTRACT_IR`
- `rtl_trace`
- `waveform_trace`
- `golden_contract_trace`
- `module_partial_sim_trace`
- `memory_trace`
- `interconnect_trace`
- `dram_trace`
- `coherence_trace`
- `atomic_trace`
- `barrier_fence_trace`
- `runtime_launch_trace`
- `assembler_trace`
- `disassembler_trace`
- `program_image_trace`
- `loader_trace`
- `toolchain_smoke_trace`

## Output IR

Produces:
- `NORMALIZED_TRACE_IR`
- `CORRECTNESS_GATE_REPORT`
- `FIRST_DIVERGENCE_REPORT`
- `PASS_EVIDENCE_REPORT`
- `TRACE_COVERAGE_REPORT`
- `PERFORMANCE_METRIC_IR`
- `REGRESSION_FINGERPRINT`
- `PERF_ATTRIBUTION_GRAPH`
- `ROOT_CAUSE_REPORT`
- `TOOLCHAIN_ATTRIBUTION_REPORT`
- `SIM_PERF_ATTRIBUTION_REPORT`

Human-facing reports:
- `VALIDATION_DASHBOARD.zh.md`
- `DEBUG_SUMMARY.zh.md` on failure or ambiguity

`FIRST_DIVERGENCE_REPORT` is required in Failure Attribution Mode.
`PASS_EVIDENCE_REPORT`, `TRACE_COVERAGE_REPORT`, and
`REGRESSION_FINGERPRINT` are required in Pass Evidence Mode.
`PERFORMANCE_METRIC_IR` is produced in both modes when trace evidence contains
cycle or order information.

## Owned Decisions

This skill owns:
- trace source ingestion and timestamp normalization
- event dictionary and trace hash construction
- event-to-contract-path mapping
- event-to-RTL-module mapping
- event-to-toolchain-artifact mapping
- correctness gate and mode selection
- first deterministic architectural divergence selection
- pass evidence and evidence completeness reporting
- trace coverage summary generation
- performance metric extraction
- bottleneck graph construction
- root cause classification
- minimal correctness and performance trace window selection
- toolchain/runtime trace attribution
- execution correctness evidence aggregation
- report generation for rewrite routing or regression tracking
- CU-level trace partitioning
- wavefront EXEC-mask diff
- divergence path diff
- memory fabric contention attribution

## Human and AI Output Policy

Normalized traces, first divergence reports, performance attribution graphs, and
root cause reports are AI-facing English artifacts. Human-facing output must be
a concise Chinese `VALIDATION_DASHBOARD.zh.md`.

On a passing run, humans should see RTL vs golden verdict, memory dump status,
coverage sufficiency, performance warnings, and regression fingerprint stability.
On failure, emit `DEBUG_SUMMARY.zh.md` with first divergence cycle, CU,
wavefront, PC,
mismatch type, likely root cause, owner, and next patch route. Pass the full
English root cause and trace artifacts to `gpgpu-loop` through
`ARTIFACT_MANIFEST_IR`.

Do not expose full traces, full `NORMALIZED_TRACE_IR`, or full
`PERF_ATTRIBUTION_GRAPH` by default unless the user asks, root cause is
ambiguous, a regression reappears, or a downstream owner needs exact fields.

## Forbidden Actions

This skill must not:
- redefine contract semantics
- redefine RTL module interfaces
- accept golden traces not derived from `GOLDEN_CONTRACT_MODEL`
- treat final memory mismatch as the root cause without causal evidence
- perform failure localization in a clean RTL/golden pass unless trace-level
  divergence exists
- emit performance root causes or architecture rewrite recommendations without
  causal graph evidence
- blame RTL decode before checking assembler, program image, loader, runtime
  launch, and first-fetch evidence when toolchain traces exist
- produce rewrite patches directly

## Required Tables

This skill must use:
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/tables/human_report_template_table.yaml`
- `shared/tables/trace_normalization_table.yaml`
- `shared/tables/correctness_gate_decision_table.yaml`
- `shared/tables/trace_source_manifest_table.yaml`
- `shared/tables/event_type_taxonomy.yaml`
- `shared/tables/stall_reason_taxonomy.yaml`
- `shared/tables/differential_compare_table.yaml`
- `shared/tables/pass_evidence_gate_table.yaml`
- `shared/tables/performance_metric_table.yaml`
- `shared/tables/bottleneck_template_table.yaml`
- `shared/tables/toolchain_attribution_taxonomy.yaml`
- `shared/tables/minimal_trace_window_table.yaml`
- `shared/tables/report_generation_table.yaml`
- `shared/tables/perf_attribution_taxonomy.yaml`
- `shared/tables/root_cause_taxonomy.yaml`
- `shared/tables/rtl_partial_sim_gate_table.yaml`
- `shared/tables/revalidation_routing_table.yaml`
- `shared/tables/rewrite_trigger_table.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/correctness_gate_report_ir.schema.yaml`
- `shared/schemas/first_divergence_report_ir.schema.yaml`
- `shared/schemas/pass_evidence_report_ir.schema.yaml`
- `shared/schemas/trace_coverage_report_ir.schema.yaml`
- `shared/schemas/performance_metric_ir.schema.yaml`
- `shared/schemas/regression_fingerprint_ir.schema.yaml`
- `shared/schemas/toolchain_attribution_report_ir.schema.yaml`
- `shared/schemas/trace_source_manifest_ir.schema.yaml`
- `shared/schemas/stall_breakdown_ir.schema.yaml`
- `shared/schemas/perf_attribution_graph.schema.yaml`
- `shared/schemas/root_cause_report_ir.schema.yaml`
- `shared/schemas/sim_perf_attribution_report_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- `CORRECTNESS_GATE_REPORT` selects exactly one mode for each run.
- RTL/golden match enters Pass Evidence Mode, not skill skip.
- RTL/golden mismatch, completion/fault mismatch, final memory mismatch, or
  trace-level architectural divergence enters Failure Attribution Mode.
- Failure Attribution Mode must prefer the first deterministic architectural
  divergence over final-state symptoms.
- Pass Evidence Mode must report evidence completeness, architectural state
  comparison, trace coverage, performance metrics, and regression fingerprint.
- `PERF_ATTRIBUTION_GRAPH` must connect cycle or order window, CU and wavefront,
  bottleneck/event evidence, contract path, and RTL module evidence when it is
  used for root cause or performance rewrite decisions.
- L3/L4 trace comparison must include CU-level trace partitioning, EXEC mask diff, wave state diff, and divergence path diff.
- Memory stall classification must distinguish coalescing stall, LDS stall, inter-CU contention, DRAM bank conflict, atomic serialization wait, and fence drain wait.
- A performance root cause without this causal chain must be
  `INSUFFICIENT_TRACE_EVIDENCE`.
- Every bottleneck node has trace evidence.
- Every root cause references contract paths, RTL module paths, toolchain
  artifact paths, or an explicit test-evidence gap.
- Toolchain root causes must reference toolchain artifact paths and
  source-of-truth checks.
- Golden trace evidence derives from `GOLDEN_CONTRACT_MODEL`.
- Golden image execution evidence derives from `PROGRAM_IMAGE_IR`.

## Failure Modes

This skill must emit:
- `TRACE_FIELD_MISSING`
- `TRACE_NORMALIZATION_FAIL`
- `GOLDEN_TRACE_UNTRUSTED`
- `TOOLCHAIN_TRACE_FIELD_MISSING`
- `GOLDEN_IMAGE_EXECUTION_MISMATCH`
- `CORRECTNESS_GATE_INSUFFICIENT_EVIDENCE`
- `TRACE_DIVERGENCE_AFTER_FINAL_MATCH`
- `FIRST_DIVERGENCE_INSUFFICIENT_TRACE`
- `PASS_EVIDENCE_INCOMPLETE`
- `PERFORMANCE_METRIC_UNAVAILABLE`
- `PERF_CAUSAL_CHAIN_MISSING`
- `TOOLCHAIN_ATTRIBUTION_AMBIGUOUS`
- `ROOT_CAUSE_AMBIGUOUS`
- `INSUFFICIENT_TRACE_EVIDENCE`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- `report_id`
- `mode`
- `correctness_verdict`
- `performance_verdict`
- `evidence_verdict`
- `normalized_trace_hash`
- `correctness_gate_report_ref`
- `first_divergence_report_ref`
- `pass_evidence_report_ref`
- `performance_metric_ref`
- `perf_attribution_graph_ref`
- `root_cause_report_ref`
- `toolchain_attribution_report_ref`
- `trace_coverage_report_ref`
- `regression_fingerprint_ref`
- `top_bottlenecks`
- `contract_path_index`
- `toolchain_artifact_path_index`
- `rtl_module_path_index`
- `evidence_hashes`
- `rewrite_handoff`
- `human_summary`
- `downstream_contract`

## Mode A: Failure Attribution Mode

Trigger:
- RTL final architectural state mismatches golden
- final memory dump mismatches golden
- completion or fault status mismatches golden
- trace-level architectural divergence exists
- contract violation is observed

Required outputs:
- `CORRECTNESS_GATE_REPORT`
- `FIRST_DIVERGENCE_REPORT`
- `PERFORMANCE_METRIC_IR`
- `PERF_ATTRIBUTION_GRAPH`
- `ROOT_CAUSE_REPORT`
- `SIM_PERF_ATTRIBUTION_REPORT`

Rules:
- Select the first deterministic architectural divergence.
- Use final memory mismatch as a symptom, not as the root cause.
- Route toolchain, runtime, RTL, memory, scheduler, and evidence causes to the
  owner skill specified by the revalidation routing table.

## Mode B: Pass Evidence Mode

Trigger:
- RTL final architectural state matches golden
- final memory dump matches golden
- completion and fault status match golden
- no architectural trace divergence is detected

Required outputs:
- `CORRECTNESS_GATE_REPORT`
- `PASS_EVIDENCE_REPORT`
- `TRACE_COVERAGE_REPORT`
- `PERFORMANCE_METRIC_IR`
- `REGRESSION_FINGERPRINT`
- `SIM_PERF_ATTRIBUTION_REPORT`

Rules:
- Do not run failure localization unless trace-level divergence exists.
- Emit `PASS_WITH_INSUFFICIENT_EVIDENCE` when hashes, traces, launch config, or
  initial/final memory evidence are incomplete.
- Emit performance warnings when metrics violate configured targets.
- Build `PERF_ATTRIBUTION_GRAPH` in performance gate or optimization tasks even
  when correctness passes.

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `trace_ingestion_and_normalization.md`
- `correctness_gate_and_mode_selection.md`
- `differential_correctness_engine.md`
- `pass_evidence_engine.md`
- `performance_metric_extractor.md`
- `bottleneck_graph_builder.md`
- `root_cause_engine.md`
- `minimal_trace_window_rules.md`
- `toolchain_trace_attribution.md`
- `report_generation_rules.md`
- `legacy_validation_and_trace_constraints.md`
- `multi_cu_trace_model.md`
- `wavefront_trace_diff.md`
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/correctness_gate_report_ir.schema.yaml`
- `shared/schemas/first_divergence_report_ir.schema.yaml`
- `shared/schemas/pass_evidence_report_ir.schema.yaml`
- `shared/schemas/trace_coverage_report_ir.schema.yaml`
- `shared/schemas/performance_metric_ir.schema.yaml`
- `shared/schemas/regression_fingerprint_ir.schema.yaml`
- `shared/schemas/toolchain_attribution_report_ir.schema.yaml`
- `shared/schemas/perf_attribution_graph.schema.yaml`
- `shared/schemas/root_cause_report_ir.schema.yaml`
- `shared/schemas/sim_perf_attribution_report_ir.schema.yaml`
- `shared/tables/trace_normalization_table.yaml`
- `shared/tables/correctness_gate_decision_table.yaml`
- `shared/tables/pass_evidence_gate_table.yaml`
- `shared/tables/performance_metric_table.yaml`
- `shared/tables/bottleneck_template_table.yaml`
- `shared/tables/toolchain_attribution_taxonomy.yaml`
- `shared/tables/minimal_trace_window_table.yaml`
- `shared/tables/report_generation_table.yaml`
- `shared/tables/perf_attribution_taxonomy.yaml`
- `shared/tables/root_cause_taxonomy.yaml`
- `shared/tests/simulation_performance_attribution_engine/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_perf_attribution_graph.yaml`

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
