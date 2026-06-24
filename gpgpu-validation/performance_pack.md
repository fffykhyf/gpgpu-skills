# Performance Pack

## Merged Source Material

### Source ID: `gpgpu-validation/bottleneck_graph_builder.md`

# Bottleneck Graph Builder

The bottleneck graph builder converts normalized events and performance metrics
into `PERF_ATTRIBUTION_GRAPH`. It supports correctness failure graphs and
performance bottleneck graphs.

## Required Causal Chain

For a performance root cause or architecture rewrite recommendation, the graph
must connect:

```text
cycle_or_order_window
  -> warp_or_block_context
  -> bottleneck_or_divergence_event
  -> RTL module path or toolchain artifact path
  -> SYSTEM_CONTRACT_IR path
```

Memory-specific chains may still use:

```text
warp_stall
  -> scoreboard_dependency
  -> lsu_lane_format / memory_tag_allocate / coalescer_merge
  -> l1_cache_hit_or_miss / l2_slice_route / mshr_replay / dram_bank_conflict
  -> rtl_memory_or_fabric_module
  -> contract_rule
```

## Node Classes

- `cycle_window`
- `order_window`
- `block`
- `warp`
- `lane`
- `instruction`
- `pc_event`
- `decode_event`
- `active_mask_event`
- `register_writeback`
- `scoreboard_dependency`
- `scheduler_state`
- `barrier_state`
- `branch_divergence`
- `memory_request`
- `memory_response`
- `lsu_lane_format`
- `memory_tag`
- `cache_event`
- `l2_slice_route`
- `mshr_replay`
- `dram_schedule`
- `bank_conflict`
- `coalescing_event`
- `atomic_serialization`
- `fence_visibility`
- `barrier_phase`
- `wsync_drain`
- `interface_backpressure`
- `rtl_pipeline_stage`
- `toolchain_artifact`
- `runtime_launch_event`
- `contract_rule`
- `bottleneck_category`

## Edge Classes

- `caused_by`
- `blocked_by`
- `waits_for`
- `violates`
- `maps_to`
- `amplified_by`
- `precedes`
- `depends_on`
- `routes_to`

## Causal Templates

The builder is template-driven. Supported templates:

- `memory_latency_template`
- `shared_bank_conflict_template`
- `scoreboard_dependency_template`
- `scheduler_underutilization_template`
- `barrier_synchronization_template`
- `branch_divergence_template`
- `pipeline_imbalance_template`
- `interface_backpressure_template`
- `toolchain_mismatch_template`
- `runtime_launch_mismatch_template`
- `coalescer_restore_mismatch_template`
- `l2_slice_route_mismatch_template`
- `mshr_replay_mismatch_template`
- `atomic_serialization_mismatch_template`
- `fence_drain_incomplete_template`

Example:

```yaml
scheduler_underutilization_template:
  nodes:
    - cycle_window
    - low_eligible_warp_count
    - scoreboard_or_barrier_or_divergence
    - scheduler_policy
    - warp_scheduler_module
    - execution_model_scheduler_contract
  edges:
    - cycle_window blocked_by low_eligible_warp_count
    - low_eligible_warp_count caused_by scoreboard_or_barrier_or_divergence
    - scoreboard_or_barrier_or_divergence maps_to warp_scheduler_module
    - warp_scheduler_module maps_to execution_model_scheduler_contract
```

Toolchain example:

```yaml
assembler_encoding_mismatch_template:
  nodes:
    - instruction_mismatch
    - encoded_instruction
    - assembler_trace
    - isa_model_instruction_encoding
    - assembler_artifact
  edges:
    - instruction_mismatch caused_by encoded_instruction
    - encoded_instruction maps_to assembler_trace
    - assembler_trace maps_to isa_model_instruction_encoding
    - assembler_trace maps_to assembler_artifact
```

## Fail-Closed Rule

If the graph cannot connect event evidence, contract path, and RTL module path
or toolchain artifact path for the selected claim, the verdict is
`INSUFFICIENT_TRACE_EVIDENCE`.

## XiangShan TopDown GPGPU Attribution

`TOPDOWN_GPGPU_ATTRIBUTION` partitions total cycles into frontend/fetch/decode
idle, warp scheduling stall, scoreboard dependency stall, memory pipeline
stall, synchronization stall, tensor/ALU busy, and structural conflict. Memory
pipeline stall must be further attributable to coalescer, L1, MSHR, NoC, L2,
DRAM, or return path when those traces exist.

### Source ID: `gpgpu-validation/memory_attribution_matrix.md`

# Memory Attribution Matrix

Memory attribution order:

1. warp transaction formation;
2. coalesced transaction count;
3. shared bank conflict;
4. L1 hit/miss/reservation status;
5. MSHR;
6. ICNT request path;
7. L2/subpartition queue;
8. DRAM queue/timing/row locality/bank skew;
9. return path;
10. scoreboard release.

### Source ID: `gpgpu-validation/multi_sm_trace_model.md`

# Multi-SM Trace Model

This file defines trace partitioning for `multi_sm_memory_path` evidence and
prepares the system for `full_memory_sync_system` memory fabric attribution.

## SM-level trace partitioning

All normalized trace events must carry:
- `run_id`
- `sm_id`
- `warp_id`
- `event_order`
- `cycle` or logical order
- `pc`
- `event_type`
- `contract_path`
- `rtl_module_path`

SM-level trace partitioning means each SM can be compared independently before
global memory, atomic, or barrier ordering is evaluated.

## Warp interleaving model

warp interleaving model:
- events are ordered per warp
- issue events are ordered per SM
- memory requests are ordered per source SM and per memory ordering scope
- L2/DRAM/atomic events may create cross-SM order constraints

Trace normalization must not assume that lower event order in one SM precedes
an unrelated event in another SM.

## Memory ordering per SM

memory ordering per SM must record:
- source SM
- warp ID
- memory space
- request sequence number
- bundle ID
- response sequence number
- fence or atomic scope

Per-SM memory order is local unless a system contract declares global, acquire,
release, atomic, or barrier constraints.

## Multi-SM Independence

multi-SM independence is the default rule:
- local warp scheduling in SM A does not constrain local scheduling in SM B
- local LDS effects are visible only inside the owner SM
- global-memory visibility follows `full_memory_sync_system` memory/coherence contracts

## Attribution Buckets

Advanced memory-path and synchronization attribution must distinguish:
- coalescing stall
- LDS stall
- inter-SM contention
- L2 queue wait
- DRAM bank conflict
- atomic serialization wait
- fence drain wait
- wave divergence attribution

## Human Dashboard

Human-facing validation dashboard should show:
- RTL vs golden verdict by SM
- top failing SM/warp
- first cross-SM ordering violation if present
- top memory-fabric bottleneck

Full per-event traces remain AI-facing artifacts.

### Source ID: `gpgpu-validation/performance_metric_extractor.md`

# Performance Metric Extractor

This component emits `PERFORMANCE_METRIC_IR` in both Failure Attribution Mode
and Pass Evidence Mode when cycle or ordered event evidence is available.

## Metric Groups

`correctness_smoke`:
- evidence completeness
- minimal fingerprint
- total cycles if available

`standard_validation`:
- basic IPC
- issue utilization
- stall breakdown
- memory latency summaries
- scheduler readiness summaries

`performance_gate`:
- full `PERFORMANCE_METRIC_IR`
- `PERF_ATTRIBUTION_GRAPH` even when correctness passes
- architecture rewrite trigger evaluation

## PERFORMANCE_METRIC_IR Shape

```yaml
performance_metric_ir:
  total_cycles: integer
  active_cycles: integer
  issue_cycles: integer
  commit_cycles: integer

  ipc: float
  warp_eligible_rate: float
  warp_issue_rate: float
  issue_utilization: float
  pipeline_utilization:
    fetch: float
    decode: float
    issue: float
    execute: float
    writeback: float
    memory: float

  stall_breakdown:
    scoreboard_dependency: integer
    no_ready_warp: integer
    memory_wait: integer
    lsq_full: integer
    coalescer_wait: integer
    bank_conflict: integer
    barrier_wait: integer
    divergence_reconvergence: integer
    register_file_port_conflict: integer
    pipeline_busy: integer
    interface_backpressure: integer
    runtime_wait: integer
    unknown: integer

  memory_metrics:
    global_memory_latency_avg: float
    global_memory_latency_p95: float
    shared_bank_conflict_rate: float
    coalescing_efficiency: float
    cache_hit_rate: optional float
    memory_replay_count: integer

  scheduler_metrics:
    ready_warp_count_avg: float
    eligible_warp_count_avg: float
    issued_warp_count: integer
    ready_but_not_issued_cycles: integer

  warning_flags:
    - LOW_ISSUE_UTILIZATION
    - HIGH_MEMORY_STALL
    - HIGH_BANK_CONFLICT
    - HIGH_INTERFACE_BACKPRESSURE
    - LOW_OCCUPANCY

  metric_groups:
    - scheduler
    - pipeline
    - memory_path
    - fabric
    - cache_mshr
    - dram
    - sync_atomic
```

## Backend PPA Evidence

Performance, FPGA, or power claims require an artifact bundle, not only a
passing simulation log.

```yaml
backend_perf_evidence:
  runtime_counter_dump: optional path
  simulator_perf_counter: optional path
  rtl_cycle_counter: optional path
  vcd_available: bool
  saif_available: bool
  synthesis_utilization_report: optional path
  timing_report: optional path
  power_report: optional path
  fpga_run_log: optional path
```

Warnings:

- `PPA_CLAIM_WITHOUT_SYNTHESIS_BUNDLE`
- `POWER_CLAIM_WITHOUT_SAIF`
- `FPGA_CLAIM_WITHOUT_BACKEND_RUN`
- `PERF_COUNTER_UNBOUND_TO_CONTRACT`

## Extraction Rules

- Use normalized event types and stall reason taxonomy only.
- If cycles are absent but order keys exist, emit ordered counts and mark rates
  as unavailable.
- Do not convert a metric warning into a root cause without bottleneck graph
  evidence.
- Preserve `performance_metric_hash` for regression fingerprinting.
- Reject PPA claims when `backend_perf_evidence` lacks the required backend
  matrix artifacts.

## XiangShan Phase Sampling Metrics

Performance gates that claim optimization must include `PHASE_FEATURE` records
unless the run is explicitly a smoke-only correctness run. A phase feature must
cover instruction mix, memory behavior, scheduling behavior, sync behavior,
cycle interval, and weight. `CHECKPOINT_PACKAGE` replay must bind golden replay,
RTL replay, counter schema, trace schema, runtime descriptor, pending
transactions, barrier state, and atomic state.

### Source ID: `gpgpu-validation/power_energy_provenance.md`

# Power / Energy Provenance

Power reports are derived evidence. They must list:

- activity counters consumed;
- counter producer status;
- sampling window;
- model mode: sim, hw, or hybrid;
- XML/config provenance if used;
- aggregation policy.

Power alone cannot prove a performance bottleneck.

### Source ID: `gpgpu-validation/queue_boundary_attribution.md`

# Queue Boundary Attribution

A memory bottleneck claim must name:

- request id or aggregate class;
- queue boundary;
- owner skill stage;
- enter and exit cycles;
- occupancy/capacity;
- release event;
- symptom counter;
- exclusion counter.

Generic `DRAM slow` or `NoC slow` labels are invalid.

### Source ID: `gpgpu-validation/report_generation_rules.md`

# Report Generation Rules

This component assembles the unified `SIM_PERF_ATTRIBUTION_REPORT` from
normalized trace, correctness gate, pass/failure evidence, metrics, causal
graph, root cause, toolchain attribution, and regression fingerprint outputs.

## Unified Report Shape

```yaml
sim_perf_attribution_report:
  report_id: string
  mode: FAILURE_ATTRIBUTION_MODE | PASS_EVIDENCE_MODE
  correctness_verdict: CORRECTNESS_PASS | CORRECTNESS_FAIL | PASS_WITH_INSUFFICIENT_EVIDENCE | PASS_WITH_PERFORMANCE_WARNING
  performance_verdict: PERFORMANCE_PASS | PERFORMANCE_WARNING | PERFORMANCE_FAIL | NOT_EVALUATED
  evidence_verdict: EVIDENCE_COMPLETE | EVIDENCE_INCOMPLETE | EVIDENCE_AMBIGUOUS

  first_divergence_report_ref: optional string
  pass_evidence_report_ref: optional string
  performance_metric_ref: optional string
  perf_attribution_graph_ref: optional string
  root_cause_report_ref: optional string
  toolchain_attribution_report_ref: optional string
  trace_coverage_report_ref: optional string
  regression_fingerprint_ref: optional string

  top_bottlenecks:
    - bottleneck_type: string
      contribution_cycles: integer
      affected_modules: list
      affected_contract_paths: list

  rewrite_handoff:
    required: bool
    patch_type: optional string
    target_skill: optional string
    required_revalidation: list

  human_summary:
    short_verdict: string
    primary_reason: string
    next_action: string
```

## Mode-Specific Rules

Failure Attribution Mode:
- include `FIRST_DIVERGENCE_REPORT`
- include `ROOT_CAUSE_REPORT` unless evidence is insufficient
- include rewrite handoff when owner and revalidation route are known

Pass Evidence Mode:
- include `PASS_EVIDENCE_REPORT`
- include `TRACE_COVERAGE_REPORT`
- include `PERFORMANCE_METRIC_IR`
- include `REGRESSION_FINGERPRINT`
- set rewrite handoff to not required unless evidence or performance warnings
  cross configured thresholds

## Human Summary Rules

- `short_verdict` must state pass, fail, insufficient evidence, or performance
  warning.
- `primary_reason` must reference the decisive report or evidence hash.
- `next_action` must name the owner skill when rewrite or evidence repair is
  required.
- Never claim a clean pass when evidence is incomplete.

## XiangShan Report Additions

Failure reports must reference `MISMATCH_PACKAGE` and
`FAILURE_CAPTURE_PACKAGE` when present. Human summaries should state replay
availability, replay command status, absent artifact reasons, suspected owner,
and required revalidation route without exposing full raw traces by default.

Performance reports must reference `WEIGHTED_PERF_REPORT` when a change claims
speedup or regression. The report must state which weighted phases changed,
which TopDown buckets moved, whether correctness diff passed first, and whether
any phase regressed enough to reject the change.

### Source ID: `gpgpu-validation/stall_reason_matrix.md`

# Stall Reason Matrix

Stall matrices must keep dimensions explicit:

- scheduler reason;
- memory access type;
- memory stall reason;
- cache request status;
- reservation fail reason;
- queue boundary;
- sync reason.

Do not collapse `cache_miss`, `cache_reservation_fail`, `mshr_fail`, and
`icnt_req_backpressure`.
