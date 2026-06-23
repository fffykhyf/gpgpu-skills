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
