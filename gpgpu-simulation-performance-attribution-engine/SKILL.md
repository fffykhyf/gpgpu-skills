---
name: gpgpu-simulation-performance-attribution-engine
description: Use when runtime, RTL, golden contract, memory, or module traces must be normalized and converted into PERF_ATTRIBUTION_GRAPH, ROOT_CAUSE_REPORT, and simulation correctness evidence.
---

# GPGPU Simulation Performance Attribution Engine

## Role

This skill normalizes traces and constructs causal performance/correctness attribution across cycle, warp, memory, contract path, and RTL module evidence.

## Position in Flow

Upstream:
- `gpgpu-system-contract-golden-engine`
- `gpgpu-incremental-rtl-binding-engine`

Downstream:
- `gpgpu-architecture-rewrite-loop-controller`

## Input IR

Consumes:
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `INCREMENTAL_RTL_MAP`
- RTL trace
- waveform-derived trace
- golden contract trace
- runtime launch trace
- memory trace
- module partial simulation trace

## Output IR

Produces:
- `NORMALIZED_TRACE_IR`
- `PERF_ATTRIBUTION_GRAPH`
- `ROOT_CAUSE_REPORT`
- `SIM_PERF_ATTRIBUTION_REPORT`

## Owned Decisions

This skill owns:
- trace normalization
- event-to-contract-path mapping
- event-to-RTL-module mapping
- bottleneck graph construction
- root cause classification
- minimal trace window selection
- execution correctness evidence aggregation

## Forbidden Actions

This skill must not:
- redefine contract semantics
- redefine RTL module interfaces
- accept golden traces not derived from `GOLDEN_CONTRACT_MODEL`
- emit performance conclusions without causal graph evidence
- produce rewrite patches directly

## Required Tables

This skill must use:
- `shared/tables/trace_normalization_table.yaml`
- `shared/tables/perf_attribution_taxonomy.yaml`
- `shared/tables/root_cause_taxonomy.yaml`
- `shared/tables/rtl_partial_sim_gate_table.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/perf_attribution_graph.schema.yaml`
- `shared/schemas/root_cause_report_ir.schema.yaml`
- `shared/schemas/sim_perf_attribution_report_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- `PERF_ATTRIBUTION_GRAPH` must connect cycle, warp, memory, contract path, and RTL module evidence.
- A performance conclusion without this causal chain must be `INSUFFICIENT_TRACE_EVIDENCE`.
- Every bottleneck node has trace evidence.
- Every root cause references contract paths or RTL module paths.
- Golden trace evidence derives from `GOLDEN_CONTRACT_MODEL`.

## Failure Modes

This skill must emit:
- `TRACE_FIELD_MISSING`
- `TRACE_NORMALIZATION_FAIL`
- `GOLDEN_TRACE_UNTRUSTED`
- `PERF_CAUSAL_CHAIN_MISSING`
- `ROOT_CAUSE_AMBIGUOUS`
- `INSUFFICIENT_TRACE_EVIDENCE`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- verdict
- normalized_trace_hash
- perf_attribution_graph_hash
- root_cause_report_hash
- minimal_trace_window
- contract_path_index
- rtl_module_path_index
- evidence_hashes
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `trace_normalizer.md`
- `bottleneck_graph_builder.md`
- `root_cause_engine.md`
- `legacy_validation_and_trace_constraints.md`
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/perf_attribution_graph.schema.yaml`
- `shared/schemas/root_cause_report_ir.schema.yaml`
- `shared/schemas/sim_perf_attribution_report_ir.schema.yaml`
- `shared/tables/trace_normalization_table.yaml`
- `shared/tables/perf_attribution_taxonomy.yaml`
- `shared/tables/root_cause_taxonomy.yaml`
- `shared/tests/simulation_performance_attribution_engine/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_perf_attribution_graph.yaml`

When a required schema, table, example, or test is missing, emit `INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
