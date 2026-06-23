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

Rocket lessons are used only for generated verification evidence: harness
closure, unit-test contracts, protocol monitors, shadow checkers, adapter
fuzzers, trace sinks, and compile-only drift coverage.

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
- `PROTOCOL_MONITOR_CONTRACT`
- `HARNESS_CLOSURE_REPORT`
- `UNIT_TEST_CONTRACT`
- `SHADOW_MEMORY_CHECKER_PLAN`
- `ADAPTER_FUZZER_PLAN`
- `TRACE_SINK_CONTRACT`
- `COMPILE_ONLY_DRIFT_EVIDENCE`
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
- `shared/references/vortex_memory_sync_lessons.yaml`

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
- `COUNTER_MANIFEST`
- `COUNTER_PRODUCER_AUDIT`
- `STALL_REASON_MATRIX`
- `MEMORY_STALL_MATRIX`
- `PERFORMANCE_ATTRIBUTION_GRAPH`
- `POWER_PROVENANCE_REPORT`
- `HARNESS_CLOSURE_EVIDENCE_REPORT`
- `ADAPTER_FUZZER_EVIDENCE_REPORT`
- `COMPILE_ONLY_DRIFT_REPORT`

Human-facing reports:
- `VALIDATION_DASHBOARD.zh.md`
- `DEBUG_SUMMARY.zh.md` on failure or ambiguity

`FIRST_DIVERGENCE_REPORT` is required in Failure Attribution Mode.
`PASS_EVIDENCE_REPORT`, `TRACE_COVERAGE_REPORT`, and
`REGRESSION_FINGERPRINT` are required in Pass Evidence Mode.
`PERFORMANCE_METRIC_IR` is produced in both modes when trace evidence contains
cycle or order information.

Additional AI-facing artifacts:
- English `COUNTER_MANIFEST.yaml`
- English `COUNTER_PRODUCER_AUDIT.md`
- English `STALL_REASON_MATRIX.csv`
- English `MEMORY_STALL_MATRIX.csv`
- English `PERFORMANCE_ATTRIBUTION_GRAPH.md`
- English `POWER_PROVENANCE_REPORT.md`
- English `ROOT_CAUSE_REPORT.md`
- English `HARNESS_CLOSURE_EVIDENCE_REPORT.md`
- English `ADAPTER_FUZZER_EVIDENCE_REPORT.md`
- English `COMPILE_ONLY_DRIFT_REPORT.md`

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
- SM-level trace partitioning
- warp EXEC-mask diff
- divergence path diff
- memory fabric contention attribution
- stable counter manifest generation
- producer audit for every stable counter
- stall reason matrix generation
- memory attribution matrix generation
- queue boundary attribution
- power and energy provenance reporting
- root cause evidence rule enforcement
- harness closure evidence ingestion
- unit-test start/finished/timeout evidence ingestion
- protocol monitor violation attribution
- shadow memory checker evidence ingestion
- adapter fuzzer pass/fail evidence ingestion
- trace sink availability and schema evidence ingestion
- compile-only drift evidence reporting

Required reference lessons:
- `VORTEX_LSU_LANE_FORMAT`
- `VORTEX_NONBLOCKING_MEMORY_TAG`
- `VORTEX_COALESCER_RESPONSE_RESTORE`
- `VORTEX_CACHE_MSHR_RESPONSE_ROUTE`
- `VORTEX_MSHR_DEADLOCK_GUARD`
- `VORTEX_BARRIER_WSYNC_DRAIN`
- `VORTEX_SIMX_RTL_TWIN`
- `ROCKET_PROTOCOL_MONITOR_CONTRACT`
- `ROCKET_HARNESS_CLOSURE_GATE`
- `ROCKET_COMPILE_ONLY_DRIFT_GATE`

## Human and AI Output Policy

Normalized traces, first divergence reports, performance attribution graphs, and
root cause reports are AI-facing English artifacts. Human-facing output must be
a concise Chinese `VALIDATION_DASHBOARD.zh.md`.

On a passing run, humans should see RTL vs golden verdict, memory dump status,
coverage sufficiency, performance warnings, and regression fingerprint stability.
On failure, emit `DEBUG_SUMMARY.zh.md` with first divergence cycle, SM,
warp, PC,
mismatch type, likely root cause, owner, and next patch route. Pass the full
English root cause and trace artifacts to `gpgpu-loop` through
`ARTIFACT_MANIFEST_IR`.

Do not expose full traces, full `NORMALIZED_TRACE_IR`, or full
`PERF_ATTRIBUTION_GRAPH` by default unless the user asks, root cause is
ambiguous, a regression reappears, or a downstream owner needs exact fields.

## Stable Counter Manifest

Every counter used for a stable conclusion must record name, producer module,
producer event, meaning, unit, sample window, status, users, and stable/debug
classification. Status is `producer-backed`, `defined-only`, or `parser-only`.

## Generator Verification Evidence Rules

This skill must ingest generator-created verification artifacts as first-class
evidence:

- harness closure proves every external port is connected to a model or tied off
- unit-test start/finished/timeout proves local block tests have deterministic
  start, finish, and timeout semantics
- protocol monitor evidence comes from `PROTOCOL_MONITOR_CONTRACT`, not
  hand-written local constants
- shadow memory checker evidence is required for memory-visible or atomic data
  changes
- adapter fuzzer evidence is required when an adapter contract is introduced or
  changed
- trace sink evidence proves runtime-visible traces have schema and consumer
  paths
- compile-only drift evidence proves named configs that do not execute still
  elaborate and retain harness collateral

Missing evidence does not become a functional root cause by itself; it routes to
test-evidence, RTL-binding, or loop rewrite triggers.

## Producer Audit

Do not treat visualizer or parser names as stable counters without producer
proof. Parser-only and defined-only counters can identify evidence gaps but
cannot be the sole basis for root cause or regression gating.

## Stall Reason Matrix

Produce scheduler and memory stall matrices with explicit dimensions. Stable
reasons include `idle_control`, `ibuffer_empty`, `simt_redirect`,
`scoreboard_wait`, `pipe_unavailable`, `barrier_wait`, `membar_wait`,
`atomic_wait`, `shared_bank_conflict`, `coalescing_stall`, `cache_miss`,
`cache_reservation_fail`, `mshr_fail`, `icnt_req_backpressure`,
`icnt_return_backpressure`, `l2_queue_full`, `dram_queue_full`,
`dram_timing_wait`, `return_path_stall`, and `scoreboard_release_wait`.

## Memory Attribution Matrix

Memory attribution must follow warp transaction formation, coalescer output,
shared bank conflict, L1 status/reservation fail, MSHR, ICNT request path, L2
queue, DRAM queue/timing/row locality/bank skew, return path, and scoreboard
release. `MISS` and `RESERVATION_FAIL` must remain separate.

## Queue Boundary Attribution

Memory bottlenecks must name the exact queue boundary and owner stage, such as
L2-to-DRAM queue, ICNT-to-shader response FIFO, or ICNT `has_buffer` injection
failure. Generic `DRAM slow`, `NoC slow`, or `memory slow` labels are invalid.

## Power / Energy Provenance

Power and energy are derivative evidence from activity counters. Power cannot
independently prove a bottleneck. Every power bucket must list consumed counters,
producer status, source mode, sample window, and model/config provenance.

## Root Cause Evidence Rule

Any root cause must include symptom counter, exclusion counter, queue/stage
owner, possible fix target, confidence, and contract or trace evidence. Missing
producer paths route to `COUNTER_SCHEMA_PATCH` or `TEST_EVIDENCE_PATCH`.

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
- ignore missing harness closure, protocol monitor, shadow checker, adapter
  fuzzer, trace sink, or compile-only drift evidence

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
- `shared/tables/verification_backend_matrix.yaml`
- `shared/tables/gpgpusim_config_taxonomy_seed.md`
- `shared/tables/stall_reason_taxonomy.md`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/protocol_monitor_contract.schema.yaml`
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
- `shared/schemas/performance_attribution_graph.schema.yaml`
- `shared/schemas/root_cause_report_ir.schema.yaml`
- `shared/schemas/sim_perf_attribution_report_ir.schema.yaml`
- `shared/schemas/counter_manifest.schema.yaml`
- `shared/schemas/stall_reason_matrix.schema.yaml`
- `shared/schemas/issue_nonissue_reason.schema.yaml`
- `shared/schemas/warp_memory_transaction.schema.yaml`
- `shared/schemas/coalescer_output_trace.schema.yaml`
- `shared/schemas/cache_request_status.schema.yaml`
- `shared/schemas/noc_packet.schema.yaml`
- `shared/schemas/memory_request_lifecycle.schema.yaml`
- `shared/schemas/memory_queue_boundary.schema.yaml`

## Required Invariants

The output must satisfy:
- `CORRECTNESS_GATE_REPORT` selects exactly one mode for each run.
- `PROTOCOL_MONITOR_CONTRACT` violations must be attributed to negotiated edge,
  adapter, module, or evidence gap before blaming memory or DRAM behavior.
- harness closure evidence is required before a full-system pass can be marked evidence-complete.
- unit-test start/finished/timeout evidence is required for unit-test pass evidence.
- protocol monitor evidence is required for negotiated interface pass evidence.
- shadow memory checker evidence is required for memory-visible data correctness.
- adapter fuzzer evidence is required for adapter pass evidence.
- trace sink evidence is required for runtime-visible trace coverage.
- compile-only drift evidence is required for named configs that are not executed.
- RTL/golden match enters Pass Evidence Mode, not skill skip.
- RTL/golden mismatch, completion/fault mismatch, final memory mismatch, or
  trace-level architectural divergence enters Failure Attribution Mode.
- Failure Attribution Mode must prefer the first deterministic architectural
  divergence over final-state symptoms.
- Pass Evidence Mode must report evidence completeness, architectural state
  comparison, trace coverage, performance metrics, and regression fingerprint.
- `PERF_ATTRIBUTION_GRAPH` must connect cycle or order window, SM and warp,
  bottleneck/event evidence, contract path, and RTL module evidence when it is
  used for root cause or performance rewrite decisions.
- Advanced memory-path and synchronization trace comparison must include SM-level trace partitioning, EXEC mask diff, warp state diff, divergence path diff, memory/fabric/cache/DRAM events, and atomic/fence/barrier/WSYNC events.
- Simulator-only gates are insufficient for FPGA-facing changes.
- Runtime launch tests must be separate from kernel functional tests.
- Synthesis/PPA evidence must be artifact-bundle based, not log-only.
- Memory stall classification must distinguish coalescing stall, LDS stall, inter-SM contention, DRAM bank conflict, atomic serialization wait, and fence drain wait.
- A performance root cause without this causal chain must be
  `INSUFFICIENT_TRACE_EVIDENCE`.
- Every bottleneck node has trace evidence.
- Every root cause references contract paths, RTL module paths, toolchain
  artifact paths, or an explicit test-evidence gap.
- Toolchain root causes must reference toolchain artifact paths and
  source-of-truth checks.
- Golden trace evidence derives from `GOLDEN_CONTRACT_MODEL`.
- Golden image execution evidence derives from `PROGRAM_IMAGE_IR`.
- Every stable counter has producer-backed, defined-only, or parser-only status.
- Root causes and regression gates must use producer-backed symptom evidence or emit an evidence/schema patch route.
- Performance attribution follows launch/occupancy, scheduler, scoreboard, SIMT, memory formation, shared bank, L1/MSHR, ICNT, L2, DRAM, return path, scoreboard release, then power derivative.
- Memory bottlenecks must cite queue-boundary evidence and exclusion counters.
- Power/energy evidence cannot be primary root-cause proof.

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
- `HARNESS_CLOSURE_EVIDENCE_MISSING`
- `UNIT_TEST_TIMEOUT_EVIDENCE_MISSING`
- `PROTOCOL_MONITOR_EVIDENCE_MISSING`
- `SHADOW_MEMORY_CHECKER_EVIDENCE_MISSING`
- `ADAPTER_FUZZER_EVIDENCE_MISSING`
- `TRACE_SINK_EVIDENCE_MISSING`
- `COMPILE_ONLY_DRIFT_EVIDENCE_MISSING`
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
- `harness_closure_evidence_ref`
- `adapter_fuzzer_evidence_ref`
- `compile_only_drift_report_ref`
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
- `multi_sm_trace_model.md`
- `warp_trace_diff.md`
- `counter_manifest_contract.md`
- `producer_audit.md`
- `stall_reason_matrix.md`
- `memory_attribution_matrix.md`
- `queue_boundary_attribution.md`
- `power_energy_provenance.md`
- `root_cause_evidence_rule.md`
- `shared/schemas/protocol_monitor_contract.schema.yaml`
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/correctness_gate_report_ir.schema.yaml`
- `shared/schemas/first_divergence_report_ir.schema.yaml`
- `shared/schemas/pass_evidence_report_ir.schema.yaml`
- `shared/schemas/trace_coverage_report_ir.schema.yaml`
- `shared/schemas/performance_metric_ir.schema.yaml`
- `shared/schemas/regression_fingerprint_ir.schema.yaml`
- `shared/schemas/toolchain_attribution_report_ir.schema.yaml`
- `shared/schemas/perf_attribution_graph.schema.yaml`
- `shared/schemas/performance_attribution_graph.schema.yaml`
- `shared/schemas/root_cause_report_ir.schema.yaml`
- `shared/schemas/sim_perf_attribution_report_ir.schema.yaml`
- `shared/schemas/counter_manifest.schema.yaml`
- `shared/schemas/stall_reason_matrix.schema.yaml`
- `shared/schemas/memory_request_lifecycle.schema.yaml`
- `shared/schemas/memory_queue_boundary.schema.yaml`
- `shared/templates/counter_manifest.md`
- `shared/templates/root_cause_report.md`
- `shared/templates/perf_root_cause_report_template.md`
- `shared/templates/memory_queue_boundary_report.md`
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
- `shared/tables/verification_backend_matrix.yaml`
- `shared/tests/simulation_performance_attribution_engine/cases.yaml`
- `shared/examples/self_correcting_minimal_simt/expected_perf_attribution_graph.yaml`

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
