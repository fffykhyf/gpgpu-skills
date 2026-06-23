# RTL Binding Core

## Merged Source Material

### Source: `skill/gpgpu-rtl/counter_tap_point_contract.md`

# Counter Tap Point Contract

Every stable counter needs a tap point:

- producer module;
- producer event;
- counter name;
- unit;
- sampling window;
- reset behavior;
- stable/debug status;
- consumer skill.

Tap points collect evidence; power or root-cause models remain outside RTL.

## Trace DB Counter Sink

Stable counters that participate in XiangShan-style structured trace must name
their `STRUCTURED_TRACE_TABLE`, write gate, schema version, and
`TRACE_DB_MANIFEST` consumer path. Debug-only counters must be marked so they do
not contaminate performance ranking.

### Source: `skill/gpgpu-rtl/hardware_rewritten_mechanism_checklist.md`

# Hardware-Rewritten Mechanism Checklist

Before binding imported evidence to RTL, confirm:

- state owner is explicit;
- interface fields are structured;
- valid/ready or request/response protocol is checked;
- fixed timing is replaced by a hardware pipeline or queue contract;
- counters have producer tap points;
- simulator-only artifacts are rejected or quarantined in compatibility notes.

### Source: `skill/gpgpu-rtl/interface_binding_and_checker.md`

# Interface Binding And Checker

The interface checker prevents incompatible RTL modules from being assembled
into a full design. Interfaces are checked as `INTERFACE_BINDING_IR`, not loose
signal maps.

## INTERFACE_BINDING_IR

Each interface binding must define:

- `interface_id`
- `producer_module`
- `consumer_module`
- `protocol`
  - `type`: `VALID_READY`, `REQ_RSP_TAGGED`, `CSR_MMIO`, or `STREAM`
- `payload`
  - `fields`
    - `name`
    - `width`
    - `signedness`
    - `semantic_path`
- `handshake`
  - `accepted_when`
  - `stall_rule`
  - `payload_stability_when_stalled`
- `ordering`
  - `in_order`
  - `tag_unique_until_response`
- `latency`
  - `min`
  - `max`
- `reset`
  - `valid_reset`
  - `ready_reset`
- `trace_tap`
  - `fire_event`
  - `payload_fields`
- `adapter`
  - `allowed`
  - `adapter_module`

## Required Checks

- producer and consumer payload fields match in name, width, signedness, and
  semantic path
- handshake protocol matches or is bridged by an explicit adapter module
- accepted transaction rule is declared
- stalled payload stability is declared and checked
- request tags are unique until response when `REQ_RSP_TAGGED` is used
- same-tag response ordering is declared
- latency bounds are compatible with pipeline boundaries
- reset values preserve legal contract state
- trace taps cover fire event and payload fields
- fault and completion propagation is declared
- CSR visibility and runtime handoff are declared for `CSR_MMIO`
- no combinational ready loop exists

## Required Identity Fields

Every scheduler, issue, writeback, memory, and trace-bearing interface must
preserve these identity fields unless the module contract proves they are not
in scope:

```yaml
required_identity_fields:
  - sm_id
  - warp_id
  - cta_or_workgroup_id
  - packet_id_or_sid
  - sop
  - eop
  - pc
  - instruction_id_or_uuid
  - exec_mask_or_tmask
```

Writeback interfaces must additionally expose:

```yaml
writeback_required_fields:
  - rd
  - dst_type
  - lane_mask
  - byte_enable_or_byte_select
  - data
  - final_packet
  - scoreboard_release_event
```

Memory request/response interfaces must additionally expose:

```yaml
memory_required_fields:
  - request_tag
  - response_tag
  - original_tag
  - lane_mask
  - byte_enable
  - per_lane_offset
  - address
  - data
  - eop
```

## Adapter Rule

An adapter is allowed only when `adapter.allowed = true` and
`adapter.adapter_module` names a catalog module with its own template, contract
paths, partial simulation cases, and timing feedback. Silent protocol coercion
is forbidden.

## Failure Modes

- `INTERFACE_PROTOCOL_MISMATCH`
- `LATENCY_INCOMPATIBLE`
- `PIPELINE_BOUNDARY_FAIL`
- `SIGNAL_WIDTH_MISMATCH`
- `BACKPRESSURE_DROP_OR_DUPLICATE`
- `TAG_REUSE_BEFORE_RESPONSE`
- `PAYLOAD_STABILITY_FAIL`
- `COMBINATIONAL_READY_LOOP`
- `FAULT_COMPLETION_PATH_UNBOUND`
- `IDENTITY_FIELD_DROPPED`
- `WRITEBACK_BYTE_ENABLE_MISSING`
- `SCOREBOARD_RELEASE_WITHOUT_FINAL_EOP`
- `COALESCER_RESPONSE_SHAPE_MISMATCH`
- `TRACE_TAP_INSUFFICIENT_FOR_FIRST_DIVERGENCE`

### Source: `skill/gpgpu-rtl/module_binding_rules.md`

# Module Binding Rules

This reference defines deterministic module-by-module RTL binding rules for
`gpgpu-rtl`. It carries forward the active rules
migrated from `gpgpu-artifact-contract-engine`, structural memory-path pieces of
`gpgpu-contract/packs/memory_path-subsystem`, runtime-interface checks, deterministic transform
checks, config checks, and implementability gates.

The Interface Contract Checker consumes these module records and rejects
incomplete load/store queue and memory-path bindings before full-system RTL
simulation.

## Deterministic Binding

`INCREMENTAL_RTL_MAP` must be derived from `SYSTEM_CONTRACT_IR`,
`GOLDEN_CONTRACT_MODEL`, `TOOLCHAIN_ARTIFACT_IR`, `PROGRAM_IMAGE_IR`,
`RUNTIME_LAUNCH_IR`, and `LOADER_CONTRACT_IR` with deterministic transforms.
Each module binding must record:

- `module_id`
- `template_id`
- `module_kind`
- consumed contract paths
- required local state
- input and output interface IDs
- local state bindings
- latency contract
- reset behavior
- local trace schema
- partial simulation cases
- timing and synthesis feedback
- source contract hash and golden-model hash
- toolchain artifact hash when the module consumes program image, runtime launch,
  or loader state

Reject magic constants, undocumented widths, unprovenanced RTL parameters,
hidden state, and cross-artifact drift. Each consumed enum, state field,
contract path, config field, and interface field must map through fixed tables.
Unused fields must be marked explicitly. Repeated runs with the same inputs must
be byte-stable or fail as nondeterministic.

## Module Binding Template

Every module record must reference a `MODULE_BINDING_TEMPLATE` from
`shared/tables/rtl_module_catalog.yaml`. A template defines:

- required contract paths
- required local state
- required input interfaces
- required output interfaces
- required partial simulation cases
- required trace fields
- forbidden hidden state
- timing checks

Required templates:

- `warp_scheduler_template`
- `scoreboard_template`
- `register_file_template`
- `lsq_template`
- `coalescer_template`
- `lds_bank_unit_template`
- `l1_cache_or_global_adapter_template`
- `memory_response_router_template`
- `fault_completion_unit_template`
- `csr_runtime_template`
- `program_image_loader_template`
- `instruction_memory_init_template`
- `runtime_arg_buffer_template`

## Required Module Decomposition

The old global RTL map is replaced by module-by-module assembly. The catalog
must include the relevant subset of:

- `sm_top`
- `warp_scheduler`
- `decode_issue_unit`
- `register_file`
- `scoreboard`
- `simt_stack`
- `load_store_queue`
- `coalescer`
- `lds_bank_unit`
- `l1_cache_or_global_adapter`
- `memory_response_router`
- `fault_completion_unit`
- `interconnect`
- `csr_runtime_interface`
- `program_image_loader_interface`
- `instruction_memory_init`
- `runtime_arg_buffer_interface`

No full-system simulation may be treated as valid until each required module
has interface evidence, partial simulation evidence, and timing feedback.

## Memory Path Structural Rules

Memory truth belongs to `SYSTEM_CONTRACT_IR`; structural realization belongs
here. Memory modules must bind:

- address-space selection
- request lifecycle
- duplicate-request prevention
- request replay policy
- coalescing lanes and masks
- byte enables
- load/store queue tags
- LDS bank selection and bank conflict stalls
- cache/global request and response protocol
- atomics and fences as contract-bound operations or reject/trap paths
- fault propagation
- completion reporting
- scoreboard wakeup
- stall and backpressure propagation

Every memory signal and tag must be traceable to a contract path or module
interface field. Structural optimizations must not change contract semantics.

## Toolchain Runtime Binding Rules

Program-image and launch artifacts are owned by
`gpgpu-toolchain-runtime`; RTL binding consumes them but does not
redefine their format.

RTL bindings must prove:

- instruction memory initialization consumes `PROGRAM_IMAGE_IR.segments[text]`
- data memory initialization consumes `PROGRAM_IMAGE_IR.segments[data]`
- entry PC comes from `LOADER_CONTRACT_IR.entry_pc_rule`
- first instruction decode uses contract-derived encoding tables
- runtime CSR writes match `RUNTIME_LAUNCH_IR.csr_write_sequence`
- argument buffer visibility matches `RUNTIME_LAUNCH_IR.arg_buffer_bytes`
- loader reset behavior matches `LOADER_CONTRACT_IR.reset_rule`

## Timing And Synthesis Feedback

Each module binding must include timing feedback hooks:

- `local_timing_risk`
- `critical_signal_paths`
- `estimated_register_count`
- `estimated_sram_macro_need`
- `fanout_risk`
- `combinational_ready_loop_check`

`combinational_ready_loop_check.no_combinational_ready_loop` must be true before
full-system assembly. A valid/ready network that forms a combinational ready
loop must fail interface checking instead of being deferred to synthesis.

## Fail Closed Rules

- Reject modules without consumed contract paths.
- Reject modules without a known binding template.
- Reject provided signals that no downstream interface consumes unless marked
  debug-only.
- Reject local state bindings that do not map to `SYSTEM_CONTRACT_IR`.
- Reject hidden state not declared in the selected template.
- Reject missing timing feedback or any combinational ready loop.

### Source: `skill/gpgpu-rtl/observable_trace_contract.md`

# Observable Trace Contract

RTL trace must expose, when implemented:

- cycle;
- core id;
- warp id;
- PC;
- active mask;
- issue valid;
- non-issue reason;
- scoreboard collision;
- selected pipe;
- memory transaction count;
- cache status;
- ICNT status;
- L2 queue status;
- DRAM queue status;
- writeback release.

These fields feed `gpgpu-validation`; they are not optional for performance claims.

## XiangShan Structured Trace Tables

When a feature affects memory, scheduling, synchronization, atomics, NoC, cache,
or performance, RTL must define a `STRUCTURED_TRACE_TABLE` with schema version,
producer, write gate, common fields, and consumer skill. Required table
families include `WARP_ISSUE_LOG`, `WARP_COMMIT_LOG`, `SCOREBOARD_LOG`,
`MEMORY_TRANSACTION_LOG`, `COALESCER_LOG`, `CACHE_ACCESS_LOG`,
`MSHR_EVENT_LOG`, `NOC_PACKET_LOG`, `BARRIER_EVENT_LOG`, `FENCE_EVENT_LOG`,
`ATOMIC_EVENT_LOG`, and `COUNTER_SNAPSHOT_LOG`.

### Source: `skill/gpgpu-rtl/partial_simulation_gates.md`

# Partial Simulation Gates

The partial simulator validates one module at a time before full-system RTL
simulation. Partial simulation is a module gate, not a replacement for
full-system verification.

## Required Inputs

- module binding record
- selected `MODULE_BINDING_TEMPLATE`
- local trace schema
- `GOLDEN_CONTRACT_MODEL` slice
- `PROGRAM_IMAGE_IR`
- `RUNTIME_LAUNCH_IR`
- `LOADER_CONTRACT_IR`
- `INTERFACE_BINDING_IR` transactions
- local stimulus

## Required Outputs

- `local_trace_hash`
- `local_scoreboard_result`
- `interface_transaction_result`
- `golden_slice_compare_result`
- `timing_feedback_result`
- `verdict`

## Module Case Requirements

`shared/tables/rtl_partial_sim_gate_table.yaml` owns the concrete case list.
At minimum it must cover:

- scoreboard: RAW dependency stall, writeback wakeup, multiple warp independence
- warp scheduler: round-robin fairness, skip stalled warp, no-ready-warp idle
- load/store queue: ready-low payload stable, tag unique, response wakeup, fault
  propagation
- LDS bank unit: bank conflict stall, lane-mask byte enable,
  aligned/misaligned behavior
- CSR runtime: start, done, fault, kernel entry, arg base
- program image loader interface: program image load, entry PC fetch, first
  instruction decode
- runtime argument buffer interface: argument buffer visible

## Gate Rule

A module with `PARTIAL_SIM_FAIL`, `INTERFACE_PROTOCOL_MICUATCH`,
`GOLDEN_SLICE_MICUATCH`, or `COMBINATIONAL_READY_LOOP` cannot be used in
full-system simulation.

Program-image and runtime partial gates also fail closed on
`PROGRAM_IMAGE_LOAD_FAIL`, `ENTRY_PC_FETCH_FAIL`, `FIRST_INSTRUCTION_DECODE_FAIL`,
or `ARG_BUFFER_VISIBILITY_FAIL`.

## Failure Evidence

Each failed case must report:

- module path
- interface ID when applicable
- contract path
- trace field
- first failing cycle when available
- expected golden slice behavior
- observed local behavior

## XiangShan Probe Gate

Partial simulation cannot sign off a feature that affects memory, scheduling,
sync, atomic, or performance unless the corresponding basic probe,
full-transaction debug probe when needed, `STRUCTURED_TRACE_TABLE`, and counter
tap ownership are present or explicitly waived with owner evidence.

### Source: `skill/gpgpu-rtl/rtl_contract_extraction_from_simulator_evidence.md`

# RTL Contract Extraction From Simulator Evidence

Rewrite simulator mechanisms into hardware contracts before binding RTL.

Can become RTL contracts:

- scoreboard pending register bitset;
- SIMT PC, active mask, and reconvergence state;
- issue gate;
- memory request interface;
- coalescer output interface;
- packet interface;
- cache status output;
- counter tap points.

Must not become RTL directly:

- C++ queue/container implementation;
- `std::set` scoreboard;
- BookSim config;
- AccelWattch object model;
- CUDA stream stack;
- fixed simulator latency;
- SM86 queue depth;
- PTX opcode latency table.

### Source: `skill/gpgpu-rtl/simulator_artifact_rejection_checklist.md`

# Simulator Artifact Rejection Checklist

Reject or quarantine:

- CUDA stream stack;
- PTX opcode latency tables;
- fixed simulator latencies;
- BookSim and local-xbar simulator assumptions;
- AccelWattch XML/object hierarchy;
- AerialVision parser-only variables;
- SM86 tested-config queue depth values.

Emit `SIMULATOR_ARTIFACT_REJECTION_REPORT` when such evidence appears.

### Source: `skill/gpgpu-rtl/sm_instance_layout.md`

# SM Instance Layout

This file defines the RTL instance layout for a SM-centric GPGPU skill system.

## SM contains

SM contains:
- N SIMD lanes
- Warp pool (resident warp slots)
- LSU front-end
- LDS SRAM
- Scheduler
- Issue Arbiter
- SGPR bank
- VGPR bank
- special-state table for EXEC/VCC/SCC/M0 or target replacement
- trace adapter

## Required RTL Modules

| Module | Responsibility |
|---|---|
| `sm_top` | Owns SM boundary, SM_ID, reset, and submodule wiring. |
| `warp_pool` | Owns resident slots, PC/base state, instruction queue, stop-fetch. |
| `warp_scheduler` | Selects a warp candidate and exposes readiness terms. |
| `sm_issue_arbiter` | Selects one or more issue records from ready candidates. |
| `decode_issue_table` | Stores typed decoded records per warp. |
| `exec_state` | Owns EXEC, VCC, SCC, and special-state files. |
| `simd_lane_cluster` | Executes vector operations under EXEC-mask gating. |
| `sgpr_bank` | Owns scalar RF storage and writeback merge. |
| `vgpr_bank` | Owns vector RF storage and lane-mask writes. |
| `lsu_frontend` | Consumes `MEMORY_BUNDLE` and emits memory-space tagged requests. |
| `lds_sram` | Implements SM-local LDS storage and bank-conflict reporting. |
| `trace_adapter` | Emits SM and warp partitioned side-effect events. |

## SM_ID routing rule

Every request, response, trace event, and performance event that can cross a SM
boundary must carry `sm_id` or a derived source ID.

Required carriers:
- dispatch packet
- instruction fetch request when shared frontend exists
- memory bundle
- L1/L2/DRAM request
- atomic request
- barrier/fence event
- trace event
- performance counter sample

## Warp dispatch mapping

Required phrase: warp dispatch mapping.

Dispatch maps workgroups and warps to SMs by an explicit rule:
- static round-robin
- occupancy-aware
- runtime-provided SM assignment
- debug-fixed SM assignment

The mapping must be recorded in the launch/runtime artifact or contract. The
RTL binding must not infer warp placement from trace ordering.

## No cross-SM dependency

Required invariant:
- no cross-SM dependency for local warp scheduler readiness
- no direct read of another SM's SGPR/VGPR/EXEC/LDS state
- no shared branch, barrier, or scoreboard table across SMs

Allowed cross-SM interactions:
- global memory fabric
- L2/DRAM ordering
- atomics at the declared serialization point
- grid-level barriers through a system synchronization contract

## Binding Checks

The RTL binding must fail if:
- a module still exposes `sm_core` as the canonical top-level execution island
- a generic scheduler is used where `warp_scheduler` is required
- memory requests lack SM_ID routing
- LDS is bound as a global-memory alias
- a single global scoreboard owns multiple SM readiness states

### Source: `skill/gpgpu-rtl/warp_exec_model.md`

# Warp Execution Model

This file defines the RTL binding contract for warp execution. It replaces
generic warp scheduler and execution pipeline language with a warp
scheduler plus SM issue model.

## Execution Granularity

Execution Granularity:
- warp = 32/64 threads
- the exact width must be a parameter from `SYSTEM_CONTRACT_IR`
- lane count must not be copied from MIAOW constants without derivation

The RTL binding must preserve:
- `sm_id`
- `warp_id`
- `pc`
- `exec_mask`
- `decoded_instruction_record`
- `issue_ready_terms`
- `memory_bundle_id` for LSU operations

## State

Required local state:
- VGPR bank
- SGPR bank
- EXEC mask register
- VCC/SCC flags
- special state table
- decoded entry valid table
- pending branch table
- memory wait table
- barrier wait table
- reconvergence stack when enabled

## EXEC-mask driven SIMD gating

SIMD lane enable must be derived from:
- current `EXEC mask register`
- instruction predicate mask
- warp lane count
- fault or trap lane suppression if present

Forbidden bindings:
- tying all lanes active because the warp is valid
- hiding lane gating inside an unnamed ALU wrapper
- treating VCC/SCC/EXEC writes as ordinary SGPR writes without special-state release evidence

## Per-warp context switching

Required phrase: per-warp context switching.

The SM issue model may switch between resident warps every issue slot.

Required binding evidence:
- warp ID selects SGPR/VGPR bases or physical banks
- issue readout selects decoded instruction record by warp ID
- special-state reads are indexed by warp ID
- LSU memory bundles carry warp ID until completion
- trace events include SM ID and warp ID

## Scoreboard interaction with EXEC mask

Required phrase: scoreboard interaction with EXEC mask.

Scoreboard readiness must combine:
- GPR readiness
- special-state readiness for EXEC/VCC/SCC/M0 or target replacement
- pending branch state
- memory wait state
- barrier wait state
- max in-flight state

EXEC writes must set and release special-state dependencies. A warp blocked
on EXEC must not issue a dependent branch, predicate, SIMD, or LSU operation.

## Partial Simulation Gate

Required partial tests:
- launch initializes EXEC
- SIMD lane gating follows EXEC
- branch or mask instruction mutates EXEC
- dependent instruction stalls until EXEC writeback release
- zero EXEC path follows contract-defined reconvergence or retirement

## Artifact Expectations

The RTL skill must produce AI-facing English artifacts:
- `INCREMENTAL_RTL_MAP`
- `MODULE_INTERFACE_REPORT`
- `RTL_PARTIAL_SIM_REPORT`

These artifacts must reference this model when binding warp scheduler,
special-state, SIMD, scoreboard, and LSU modules.
