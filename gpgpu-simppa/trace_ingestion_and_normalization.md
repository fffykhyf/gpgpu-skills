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
  event_type: fetch | decode | issue | execute | writeback | commit | branch | divergence | barrier | scoreboard_stall | memory_request | memory_response | csr_write | runtime_start | runtime_done | assembler_encode | disassembler_decode | program_image_load | loader_init | fault
  timestamp_kind: cycle | step_id | order_key
  cycle: optional integer
  step_id: optional integer
  order_key: optional string

  block_id: optional integer
  warp_id: optional integer
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
    - request_tag
    - response_tag
    - address
    - byte_enable
    - data
    - lane_mask
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
