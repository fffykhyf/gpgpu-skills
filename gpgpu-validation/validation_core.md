# Validation Core

## Merged Source Material

### Source ID: `gpgpu-validation/correctness_gate_and_mode_selection.md`

# Correctness Gate and Mode Selection

This component runs immediately after trace ingestion. It compares observable
golden and RTL outcomes, decides the run mode, and emits
`CORRECTNESS_GATE_REPORT`.

## Inputs

- `golden_final_state`
- `rtl_final_state`
- `golden_memory_dump`
- `rtl_memory_dump`
- `golden_completion_status`
- `rtl_completion_status`
- `golden_fault_status`
- `rtl_fault_status`
- optional `golden_trace`
- optional `rtl_trace`
- program image, contract, launch config, and initial memory hashes

## Output

```yaml
correctness_gate_report:
  verdict: CORRECTNESS_PASS | CORRECTNESS_FAIL | PASS_WITH_INSUFFICIENT_EVIDENCE | PASS_WITH_TRACE_DIVERGENCE_WARNING
  selected_mode: PASS_EVIDENCE_MODE | FAILURE_ATTRIBUTION_MODE
  comparison_scope:
    - final_memory
    - architectural_state
    - completion_fault
    - sampled_trace
    - instruction_trace
  mismatch_summary:
    memory_mismatch: bool
    register_mismatch: bool
    pc_mismatch: bool
    active_mask_mismatch: bool
    csr_mismatch: bool
    fault_mismatch: bool
    completion_mismatch: bool
  evidence_completeness:
    golden_trace_present: bool
    rtl_trace_present: bool
    program_image_hash_match: bool
    contract_hash_match: bool
    launch_config_hash_match: bool
    initial_memory_hash_match: bool
  fail_reason: optional string
```

## Mode Selection Rules

```text
if final memory mismatch:
    FAILURE_ATTRIBUTION_MODE
else if completion/fault mismatch:
    FAILURE_ATTRIBUTION_MODE
else if architectural state mismatch:
    FAILURE_ATTRIBUTION_MODE
else if trace-level architectural divergence exists:
    FAILURE_ATTRIBUTION_MODE
else if evidence incomplete:
    PASS_EVIDENCE_MODE with PASS_WITH_INSUFFICIENT_EVIDENCE
else:
    PASS_EVIDENCE_MODE with CORRECTNESS_PASS
```

If final memory matches but trace-level architectural divergence exists, select
Failure Attribution Mode. If the divergence is real but final outputs match,
the report may use `PASS_WITH_TRACE_DIVERGENCE_WARNING` as the correctness
verdict while still requiring `FIRST_DIVERGENCE_REPORT`.

## Fail-Closed Rules

- Do not infer correctness pass from final memory alone when completion, fault,
  launch, or contract hashes are missing.
- Do not run failure localization for a clean pass.
- Do not route to rewrite when evidence is incomplete; route to
  `TEST_EVIDENCE_PATCH` through pass evidence or root cause reporting.

## XiangShan Probe Mode Policy

`BASIC_DIFF_TRACE` is required for every correctness gate. It carries warp
commit, lane writeback, trap/fault, and launch done events. Select
`FULL_TRANSACTION_DIFF_TRACE` only when debug mode is requested, basic diff
identifies a memory/sync/control ambiguity, or a prior regression requires
transaction-level replay. Full diff must not be silently enabled in performance
ranking runs without marking the run as debug-contaminated.

### Source ID: `gpgpu-validation/counter_manifest_contract.md`

# Stable Counter Manifest

Every counter must record:

- counter name;
- producer module;
- producer event;
- meaning;
- unit;
- sample window;
- status: `producer-backed`, `defined-only`, or `parser-only`;
- used by;
- stable or debug.

Stable root-cause and regression claims require producer-backed counters.

### Source ID: `gpgpu-validation/minimal_trace_window_rules.md`

# Minimal Trace Window Rules

This file defines how correctness and performance windows are selected for
reports and rewrite handoff.

## Correctness Window

Used for RTL/golden mismatch:

```text
window_start = first_divergence_cycle - pre_window
window_end   = first_divergence_cycle + post_window
```

Required contents:
- last matching event
- first mismatching event
- all direct dependency events
- related contract paths
- related RTL module paths
- related toolchain artifact paths when present
- evidence hashes

Default rule:

```yaml
correctness_window_rule:
  pre_events: 8
  post_events: 8
  include_last_matching_event: true
  include_first_mismatching_event: true
  include_dependency_closure: true
  include_contract_path: true
  include_rtl_module_path: true
  include_toolchain_artifact_path: true
```

## Performance Window

Used for bottleneck attribution:

```text
select the continuous window with the highest stall-cycle contribution;
if several windows are close, choose the earliest one with the most complete
evidence.
```

Default rule:

```yaml
performance_window_rule:
  candidate_windows:
    - top_stall_contribution_window
    - sustained_bottleneck_window
    - queue_saturation_window
    - periodic_replay_window
  tie_breakers:
    - highest_evidence_completeness
    - earliest_window
    - strongest_contract_mapping
    - strongest_rtl_module_mapping
```

## Fail-Closed Rules

- Do not expand the window to the whole trace unless causal closure requires it.
- Do not drop direct dependency events to make a window smaller.
- Mark the window `AMBIGUOUS_TRACE_ORDERING` when event order cannot be ranked.

## XiangShan Replay Window Rules

`REPLAY_WINDOW` is required whenever `MISMATCH_PACKAGE` or
`FAILURE_CAPTURE_PACKAGE` is emitted. The window must name the trigger, start
cycle, end cycle, pre-failure cycles, post-failure cycles, and optional
checkpoint id. Batch capture should keep the window bounded; interactive replay
may request additional windows only through explicit debug commands.

### Source ID: `gpgpu-validation/pass_evidence_engine.md`

# Pass Evidence Engine

This component is required only in Pass Evidence Mode. It proves that a pass is
credible enough for regression tracking and performance comparison.

## Trigger

- RTL final architectural state matches golden
- final memory dump matches golden
- completion and fault status match golden
- no architectural trace divergence is detected

## Required Outputs

- `PASS_EVIDENCE_REPORT`
- `TRACE_COVERAGE_REPORT`
- `REGRESSION_FINGERPRINT`

## PASS_EVIDENCE_REPORT Shape

```yaml
pass_evidence_report:
  verdict: CORRECTNESS_PASS_STRONG | CORRECTNESS_PASS_WEAK | PASS_WITH_INSUFFICIENT_EVIDENCE | PASS_WITH_PERFORMANCE_WARNING | PASS_WITH_TRACE_DIVERGENCE_WARNING
  evidence_completeness:
    system_contract_hash: string
    golden_model_hash: string
    rtl_hash: string
    toolchain_artifact_hash: optional string
    program_image_hash: optional string
    runtime_launch_hash: optional string
    input_memory_hash: string
    final_memory_hash: string
    golden_trace_present: bool
    rtl_trace_present: bool
    completion_status_present: bool
    fault_status_present: bool
  architectural_state_comparison:
    final_memory_match: bool
    final_pc_match: bool
    observable_register_state_match: bool
    csr_state_match: bool
    fault_status_match: bool
    completion_status_match: bool
  coverage_summary_ref: TRACE_COVERAGE_REPORT
  performance_metric_ref: PERFORMANCE_METRIC_IR
  regression_fingerprint_ref: REGRESSION_FINGERPRINT
  warnings:
    - uncovered_contract_paths
    - insufficient_trace_detail
    - performance_below_target
    - unstable_trace_hash
```

## Pass Strength

`CORRECTNESS_PASS_STRONG` requires:

- final state match
- completion/fault match
- trace schema complete
- first-divergence diff clean
- required backend matrix passed

`CORRECTNESS_PASS_WEAK` means:

- final state matches
- trace misses key fields, runtime launch evidence is incomplete, or backend
  matrix is incomplete

Weak pass is valid for local iteration but cannot support FPGA, PPA, or release
claims.

## REGRESSION_FINGERPRINT Shape

```yaml
regression_fingerprint:
  contract_hash: string
  golden_model_hash: string
  rtl_hash: string
  toolchain_artifact_hash: optional string
  program_image_hash: optional string
  runtime_launch_hash: optional string
  loader_contract_hash: optional string
  input_memory_hash: string
  final_memory_hash: string
  trace_summary_hash: string
  performance_metric_hash: string
  coverage_hash: string
```

## Coverage Rules

`TRACE_COVERAGE_REPORT` must record:
- observed contract paths
- unobserved required contract paths
- observed RTL module paths
- observed toolchain artifact paths
- source completeness by trace type
- coverage hash

## Warning Rules

- `PASS_WITH_INSUFFICIENT_EVIDENCE`: final outputs match but required hashes,
  traces, launch config, or completion/fault evidence are missing.
- `PASS_WITH_PERFORMANCE_WARNING`: correctness passes but metrics violate target
  thresholds.
- `PASS_WITH_TRACE_DIVERGENCE_WARNING`: final outputs match but architectural
  traces diverge. This escalates to Failure Attribution Mode for first
  divergence reporting.

## XiangShan Capture Evidence

Passing CI evidence may include `BATCH_AUTO_CAPTURE` disabled by policy, but
failure evidence must include `FAILURE_CAPTURE_PACKAGE` or an explicit
test-evidence gap. A failure package must include replay command, trace slice,
waveform slice or absent reason, config hash, program image hash, golden state,
RTL state summary, memory store log, counter snapshot, and normalized report.

### Source ID: `gpgpu-validation/producer_audit.md`

# Producer Audit

Audit every counter before use:

1. Find the producer event path.
2. Confirm update/reset/sample window.
3. Classify status.
4. Reject parser-only variables for stable gates.
5. Mark defined-only counters as evidence gaps.

Visualizer names are not stable metrics without producer proof.

## Structured Trace Producer Audit

For each `STRUCTURED_TRACE_TABLE`, audit table producer module, producer event,
write gate, schema version, sample window, and consumer skill. A table without
producer proof can support exploratory debug only; it cannot close
`SQL_PERF_QUERY` attribution or weighted performance gates.

### Source ID: `gpgpu-validation/trace_ingestion_and_normalization.md`

# Trace Ingestion and Normalization

This component replaces the old trace normalizer. It accepts multi-source
simulation, golden, runtime, memory, module, waveform, and toolchain evidence
and emits `NORMALIZED_TRACE_IR`.

## Supported Trace Sources

- `rtl_trace`
- `waveform_trace`
- `golden_contract_trace`
- `module_partial_sim_trace`
- `memory_trace`
- `runtime_launch_trace`
- `assembler_trace`
- `disassembler_trace`
- `program_image_trace`
- `loader_trace`
- `toolchain_smoke_trace`

## Responsibilities

- normalize time bases into `cycle`, `step_id`, or deterministic `order_key`
- normalize field names across RTL, golden, waveform, memory, runtime, and
  toolchain sources
- generate a stable event dictionary
- map each event to `contract_path`
- map RTL evidence to `rtl_module_path`
- map toolchain evidence to `toolchain_artifact_path`
- attach source hashes and event-level `evidence_hash`
- detect missing required fields before downstream attribution
- produce a `trace_summary_hash` suitable for regression fingerprinting

## Normalized Event Fields

Each event in `NORMALIZED_TRACE_IR.events` should use this field vocabulary:

```yaml
event:
  event_id: string
  event_source: rtl_trace | golden_trace | waveform_trace | memory_trace | runtime_trace | assembler_trace | disassembler_trace | program_image_trace | loader_trace | toolchain_smoke_trace
  event_type: fetch | decode | issue | execute | writeback | commit | branch | divergence | barrier | scoreboard_stall | memory_request | memory_response | lsu_lane_format | memory_tag_allocate | memory_tag_release | coalescer_merge | coalescer_restore | l1_cache_hit | l1_cache_miss | l2_slice_route | l2_cache_hit | l2_cache_miss | mshr_allocate | mshr_replay | dram_schedule | dram_bank_conflict | atomic_serialize | atomic_visibility | fence_drain_begin | fence_drain_end | barrier_arrive | barrier_release | wsync_drain_begin | wsync_drain_end | csr_write | runtime_start | runtime_done | assembler_encode | disassembler_decode | program_image_load | loader_init | fault
  timestamp_kind: cycle | step_id | order_key
  cycle: optional integer
  step_id: optional integer
  order_key: optional string

  block_id: optional integer
  sm_id: optional integer
  warp_id: optional integer
  instruction_uuid: optional string
  lane_id: optional integer
  thread_id: optional integer
  lane_mask: optional string

  pc: optional string
  next_pc: optional string
  instruction_id: optional string
  opcode: optional string
  encoded_instruction: optional string
  decoded_instruction: optional string

  active_mask: optional string
  predicate_mask: optional string
  stall_reason: optional string
  issue_valid: optional bool
  commit_valid: optional bool

  src_regs: optional list
  dst_regs: optional list
  reg_values_before: optional map
  reg_values_after: optional map

  memory_space: optional string
  memory_addr: optional string
  access_size: optional integer
  byte_enable: optional string
  request_tag: optional string
  response_tag: optional string
  original_tag: optional string
  coalesced_tag: optional string
  per_lane_offset: optional map
  restored_lane_mask: optional string
  final_eop: optional bool
  l1_cache_id: optional string
  l2_slice_id: optional string
  cache_bank_id: optional string
  mshr_id: optional string
  fabric_route_id: optional string
  virtual_channel: optional string
  dram_channel_id: optional string
  dram_bank_id: optional string
  dram_row_id: optional string
  queue_occupancy: optional integer
  arbitration_wait_cycles: optional integer
  serialization_point: optional string
  serialization_sequence: optional integer
  fence_scope: optional string
  visibility_event: optional string
  barrier_id: optional string
  barrier_phase: optional string
  arrival_bitmap: optional string
  release_bitmap: optional string
  memory_latency: optional integer
  fault_code: optional string

  csr_addr: optional string
  csr_value: optional string
  launch_state: optional map

  contract_path: string
  rtl_module_path: optional string
  toolchain_artifact_path: optional string
  dependencies: list
  evidence_hash: string
```

## Minimum Trusted Trace Fields

Trace diff is trusted only after the normalized trace carries this minimum
schema:

```yaml
minimum_trusted_trace_fields:
  identity:
    - cycle
    - uuid_or_instruction_id
    - sm_id
    - warp_id
    - cta_or_workgroup_id
    - packet_id_or_sid
    - sop
    - eop
  instruction:
    - pc
    - encoded_instruction
    - decoded_instruction
    - opcode
    - fu_type
  mask:
    - exec_mask_or_tmask
    - predicate_mask
  writeback:
    - rd
    - dst_type
    - byte_enable_or_byte_select
    - dst_data
  memory:
    - instruction_uuid
    - request_tag
    - response_tag
    - original_tag
    - coalesced_tag
    - address
    - byte_enable
    - per_lane_offset
    - data
    - lane_mask
    - restored_lane_mask
    - final_eop
  fabric_cache_dram:
    - l1_cache_id
    - l2_slice_id
    - cache_bank_id
    - mshr_id
    - fabric_route_id
    - virtual_channel
    - dram_channel_id
    - dram_bank_id
    - dram_row_id
    - queue_occupancy
    - arbitration_wait_cycles
  sync_atomic:
    - serialization_point
    - serialization_sequence
    - fence_scope
    - visibility_event
    - barrier_id
    - barrier_phase
    - arrival_bitmap
    - release_bitmap
  scheduler:
    - ready
    - stalled
    - stall_reason
    - scoreboard_busy
  barrier:
    - barrier_id
    - phase
    - arrive
    - wait
    - release
```

If trace lacks `byte_enable`, packet/EOP identity, or request/response tags,
it cannot high-confidence localize register-file, scoreboard, coalescer, cache
replay, or response-restore failures. Emit `PASS_WITH_INSUFFICIENT_EVIDENCE`
or `TRACE_FIELD_MISSING` rather than a strong pass.

Memory/fabric/synchronization traces must retain Vortex-derived identities:
original and coalesced tags, source SM, warp/lane shape, L2 slice route, MSHR
ID, queue occupancy, atomic serialization point, fence visibility event,
barrier phase, and WSYNC drain release. Dropping these fields makes the event
usable for performance summaries only, not for high-confidence root cause.

## Source Rules

- Golden events must derive from `GOLDEN_CONTRACT_MODEL`.
- Golden image execution events must fetch and decode from `PROGRAM_IMAGE_IR`.
- Toolchain events must identify assembler, disassembler, program image,
  loader, runtime launch, or toolchain smoke artifact path.
- RTL events must identify a module path from `INCREMENTAL_RTL_MAP` whenever a
  module mapping exists.
- Runtime launch events must identify launch config, arg buffer, CSR start,
  done, and fault observation evidence when present.
- Events without cycle information must provide a deterministic `order_key`.
- Missing fields become `TRACE_FIELD_MISSING` or
  `TOOLCHAIN_TRACE_FIELD_MISSING`, not guessed values.

## Trace Hash Rules

`NORMALIZED_TRACE_IR` must contain:
- `trace_id`
- `trace_source_manifest_ref`
- `event_dictionary`
- `event_to_contract_path_map`
- `event_to_toolchain_artifact_path_map`
- `event_to_rtl_module_map`
- `timestamp_normalization_report`
- `trace_summary_hash`
- per-source hashes for regression fingerprinting

## XiangShan Structured Trace Input

When `XIANGSHAN_STRUCTURED_TRACE_DB` is enabled, ingestion must accept
`TRACE_DB_MANIFEST`, validate every `STRUCTURED_TRACE_TABLE` schema version, and
preserve SQL query artifacts as evidence:

- `SQL_DEBUG_QUERY` for first-divergence/root-cause investigation
- `SQL_PERF_QUERY` for performance attribution

Default table families include warp issue/commit, scoreboard, memory
transaction, coalescer, cache access, MSHR event, NoC packet, barrier, fence,
atomic, runtime launch, fault, and counter snapshot logs.
