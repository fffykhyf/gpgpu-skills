# Interconnect Contract Pack

Preserved concepts: `source_sm_id`, `request_tag`, `source_request_tag`, `traffic_class`, `target_l2_slice_id`, `final_eop`, SM to L2 routing table, NoC routing, fabric queue backpressure, L2 subpartition queue, response demux target, return path, DRAM scheduler boundary, and address mapping evidence.

## When to Load

Load when `CAPABILITY_PROFILE_IR.enabled_packs` includes `interconnect`, or when the design requires multi-SM routing, NoC/fabric routing, L2 slice routing, fabric backpressure, request/response routing, or DRAM scheduler boundary evidence.

## Owned Contract Fragments

Own only the contract fragments named by this pack. The frozen truth remains `SYSTEM_CONTRACT_IR`; pack details must become explicit contract paths before RTL or toolchain use.

## Compact Provenance

Merged source IDs in this pack have provenance
`merged_into_current_pack`. A loader must not expect separate source files for
those IDs unless a real `shared/` or pack-local path is listed below.

## Claim Boundary

Do not claim complete response queue behavior, full MSHR routing, complete
memory ordering, dirty writeback handling, or coherence behavior from
interconnect evidence alone. Those claims require explicit contract ownership
and validation evidence from the relevant memory or synchronization pack.

## SM to Memory Fabric

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Packet Format

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Fabric Request/Response Contract

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## NoC Routing

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## SM to L2 Slice Routing

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## L2 Subpartition Queue

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Backpressure

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Response Demux and Return Path

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## DRAM Scheduler Boundary

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Address Mapping Evidence

Preserve the merged source rules below and bind every generated artifact to explicit contract paths and evidence.

## Golden Semantics Hooks

Expose hook names and state transitions for deriving `GOLDEN_CONTRACT_MODEL` only from `SYSTEM_CONTRACT_IR`.

## RTL Binding Hooks

Expose contract paths, negotiated interface edges, trace events, and counter tap points that RTL may bind without inventing semantics.

## Validation Gates

Require compact pass evidence, first-divergence capture when mismatched, and regression fingerprints for the touched contract paths.

## Failure Modes

Reject missing provenance, simulator-only behavior, unowned semantics, unobservable state transitions, and outputs that bypass `RUN_STATE.yaml`.

## Merged Source Material

### Source ID: `gpgpu-contract/packs/interconnect/SKILL.md`

---
name: gpgpu-contract/packs/interconnect
description: Use when SM memory requests must be routed through NoC, L1/L2 fabric, cross-SM queues, congestion models, or SM-to-memory fabric contracts before DRAM, coherence, atomic, or fence behavior is evaluated.
---

# GPGPU Interconnect Contract Engine

## Role

This skill defines the `full_memory_sync_system` interconnect contract between SM-local memory
front-ends and the shared memory hierarchy. It owns NoC routing, SM-to-L2
mapping, request queues, fabric arbitration, and congestion evidence.

Rocket lessons are used here only for negotiated interface, adapter, and
protocol-monitor structure. TileLink is not mandatory; the required abstraction
is a negotiated edge with explicit adapter and monitor contracts.

## Position in Flow

Upstream:
- `gpgpu-architecture`
- `gpgpu-toolchain-runtime`
- `gpgpu-rtl`

Downstream:
- `gpgpu-contract`
- `gpgpu-contract/packs/memory_path`
- `gpgpu-contract/packs/atomic_sync`
- `gpgpu-validation`
- `gpgpu-loop`

## Input IR

Consumes:
- `ARCH_IR`
- `CAPABILITY_PROFILE_IR`
- `INCREMENTAL_RTL_MAP`
- `RESOLVED_CONFIG_IR`
- `SYSTEM_COMPOSITION_IR`
- optional `NEGOTIATED_INTERFACE_IR`
- `MEMORY_BUNDLE`
- per-SM trace partitions
- memory hierarchy constraints
- `shared/references/source_summaries/vortex.md`

## Output IR

Produces:
- `NEGOTIATED_INTERFACE_IR`
- `ADAPTER_CONTRACT`
- `PROTOCOL_MONITOR_CONTRACT`
- `CONTRACT_FRAGMENT_IR`
- `NOC_ROUTING_CONTRACT`
- `SM_TO_MEMORY_FABRIC_IR`
- `FABRIC_CONTENTION_REPORT`
- `MEMORY_REQUEST_QUEUE_REPORT`
- `NOC_PACKET_SPEC`
- `ICNT_BACKPRESSURE_SPEC`
- `L2_SUBPARTITION_QUEUE_SPEC`
- `DRAM_SCHEDULER_SPEC`
- `ADDRESS_MAPPING_EVIDENCE`
- `RETURN_PATH_SPEC`

Human-facing report:
- interconnect section in `VALIDATION_DASHBOARD.zh.md`

AI-facing artifacts:
- English `NEGOTIATED_INTERFACE_IR.yaml`
- English `ADAPTER_CONTRACT.yaml`
- English `PROTOCOL_MONITOR_CONTRACT.yaml`
- English `NOC_ROUTING_CONTRACT.yaml`
- English `SM_TO_MEMORY_FABRIC_IR.yaml`
- English `FABRIC_CONTENTION_REPORT.yaml`
- English `MEMORY_REQUEST_QUEUE_REPORT.yaml`
- English `NOC_PACKET_SPEC.md`
- English `ICNT_BACKPRESSURE_SPEC.md`
- English `L2_SUBPARTITION_QUEUE_SPEC.md`
- English `DRAM_SCHEDULER_SPEC.md`
- English `ADDRESS_MAPPING_EVIDENCE.md`
- English `RETURN_PATH_SPEC.md`

## Owned Decisions

This skill owns:
- SM to L2 routing table
- memory request queue per SM
- fabric arbitration policy
- NoC latency model
- congestion model
- request merging across SM
- L2 cache slicing policy handoff
- source SM ID preservation
- fabric trace event schema
- packet contract
- ICNT buffer and backpressure contract
- L2 subpartition queue contract
- DRAM-facing queue boundary handoff
- address mapping evidence contract
- return path contract
- negotiated edge ownership for SM/L1/NoC/L2/DRAM/host-facing memory paths
- width adapter, fragment adapter, source-id adapter, atomic adapter, and protocol bridge adapter selection
- protocol monitor generation from negotiated edge facts
- raw wire binding rejection before RTL binding

Required reference lessons:
- `VORTEX_CACHE_MSHR_RESPONSE_ROUTE`
- `VORTEX_SIMX_RTL_TWIN`
- `ROCKET_NEGOTIATED_INTERFACE_EDGE`
- `ROCKET_INTERFACE_ADAPTER_CONTRACT`
- `ROCKET_PROTOCOL_MONITOR_CONTRACT`
- `XIANGSHAN_STRUCTURED_TRACE_DB`

## Human and AI Output Policy

NoC and fabric contracts are AI-facing English artifacts. Human-facing output is
limited to Chinese dashboard status: routing verdict, top congested link,
affected SM IDs, request merging status, and required revalidation.

All full routing tables and queue traces must be registered in
`ARTIFACT_MANIFEST_IR`.

## Packet Contract

Every fabric packet must expose packet class, source, destination, request or
response direction, byte size, flit count, `has_buffer` result, queue enter
cycle, and queue exit cycle.

## Negotiated Interface and Adapter Rules

Every interconnect boundary must emit `NEGOTIATED_INTERFACE_IR` before packet or
wire binding. The negotiated edge derives address width, data width, source ID
width, sink ID width, size width, beat bytes, max transfer bytes, legal request
classes, legal response classes, ordering scope, denial policy, error policy,
and response shape.

raw wire binding is forbidden unless it comes from a negotiated edge.

Adapter rules:

- A width adapter is mandatory when endpoint data width or beat bytes differ.
- A fragment adapter is mandatory when transfer-size or burst-shape lattices
  differ and reassembly is required.
- A source-id adapter is mandatory when outstanding request capacity must be
  remapped or compressed.
- An atomic adapter is mandatory when an atomic operation is exposed over a path
  that does not natively support the required operation.
- A protocol bridge adapter is mandatory when crossing protocol families; it
  must document ID mapping, burst translation, response/error mapping, and
  ordering guarantees.
- Every adapter emits `ADAPTER_CONTRACT` and every external or multibeat edge
  emits `PROTOCOL_MONITOR_CONTRACT`.

## ICNT Buffer / Backpressure Contract

ICNT attribution must distinguish request packet volume, response packet volume,
request `has_buffer` failure, response FIFO full, L2-to-ICNT queue full, and
ICNT-to-shader congestion. Do not report only `NoC slow`.

## L2 Subpartition Queue Contract

L2/subpartition evidence must name source SM, destination slice/subpartition,
queue name, occupancy/capacity, hit/miss result, L2-to-DRAM event, and return
queue event.

## DRAM Queue / Scheduler Contract

This skill may report DRAM-facing queue boundaries but must not define DRAM
scheduling truth. It must pass L2-to-DRAM queue occupancy, arrival order, queue
enter/exit cycles, and address mapping fields to `gpgpu-contract/packs/memory_path`.

## Address Mapping Evidence Contract

Bank skew, row locality, and partition imbalance claims require address mapping
evidence: physical address, partition/channel, L2 slice, bank, bank group when
present, row, column, and hashing/indexing provenance.

## Return Path Contract

Return path attribution must separate DRAM-to-L2, L2-to-ICNT, ICNT-to-shader,
cluster/LSU response FIFO, and scoreboard release. Return congestion is distinct
from request injection pressure.

## Forbidden Actions

This skill must not:
- define DRAM bank scheduling
- define cache coherence semantics
- define atomic serialization semantics
- define barrier or fence semantics
- mutate `SYSTEM_CONTRACT_IR`
- hide source SM IDs in global memory traces
- allow raw wire binding without `NEGOTIATED_INTERFACE_IR`
- treat TileLink as the mandatory GPGPU fabric protocol

## Required Tables

This skill must use:
- `shared/tables/workflow_policy.yaml`
- `shared/tables/rewrite_rules.yaml`
- `shared/tables/performance_taxonomy.yaml`

## Required Schemas

This skill must validate:
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/negotiated_interface_ir.schema.yaml`
- `shared/schemas/adapter_contract.schema.yaml`
- `shared/schemas/protocol_monitor_contract.schema.yaml`
- `shared/schemas/incremental_rtl_map.schema.yaml`
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/contract_fragment_ir.schema.yaml` (`STRUCTURED_TRACE_TABLE`)
- `shared/schemas/noc_packet.schema.yaml`
- `shared/schemas/memory_queue_boundary.schema.yaml`
- `shared/schemas/structured_trace_table.schema.yaml`

## Required Invariants

The output must satisfy:
- every interconnect boundary has a `NEGOTIATED_INTERFACE_IR` edge before RTL or packet binding
- raw wire binding is forbidden unless it comes from a negotiated edge
- every width mismatch has a width adapter or a hard failure
- every transfer-size or burst-shape mismatch has a fragment adapter or a hard failure
- every source-ID compression has a source-id adapter with remap state and inflight guards
- every exposed atomic path has native support or an atomic adapter with checked preconditions
- every protocol-family crossing has a protocol bridge adapter with ID, burst, error, and ordering translation
- every negotiated edge with outstanding, multibeat, or external traffic has a `PROTOCOL_MONITOR_CONTRACT`
- every memory request entering the fabric has a `sm_id`
- every route names source SM, destination L2 slice or memory target, arbitration class, and ordering scope
- request merging across SM is explicit and never changes memory visibility
- congestion evidence maps to links, queues, and source SMs
- NoC bottlenecks must state request/response packet volume, has-buffer failure, or return FIFO pressure.
- DRAM bottleneck claims must be handed off with row locality, bank skew, queue occupancy, or address mapping evidence rather than asserted generically.
- Request path and return path must remain separately attributable.
- complete response queue, full MSHR, dirty writeback, coherence, and complete
  memory-ordering claims require explicit downstream contract and validation
  evidence
- interconnect artifacts preserve `ARTIFACT_MANIFEST_IR` provenance

## Failure Modes

This skill must emit:
- `NOC_ROUTE_MISSING`
- `SM_ID_ROUTE_MISSING`
- `FABRIC_ARBITRATION_AMBIGUOUS`
- `NEGOTIATED_EDGE_MISSING`
- `RAW_WIRE_BINDING_FORBIDDEN`
- `ADAPTER_CONTRACT_MISSING`
- `PROTOCOL_MONITOR_MISSING`
- `REQUEST_QUEUE_OVERFLOW`
- `CROSS_SM_MERGE_UNSAFE`
- `CONGESTION_MODEL_MISSING`
- `INSUFFICIENT_SKILL_ASSET`

## Report Schema

The report must include:
- verdict
- system_contract_ir_hash
- incremental_rtl_map_hash
- routing_contract_hash
- negotiated_interface_ir_hash
- adapter_contract_hash
- protocol_monitor_contract_hash
- sm_to_memory_fabric_hash
- route_results
- queue_results
- congestion_results
- affected_sm_ids
- downstream_contract

## Compact Coverage Required

This compact pack is incomplete unless these merged source IDs are present below:
- `noc_routing_contract`
- `sm_to_memory_fabric`
- `packet_contract`
- `icnt_backpressure_contract`
- `l2_subpartition_queue_contract`
- `dram_scheduler_boundary_contract`
- `address_mapping_evidence_contract`
- `return_path_contract`

It must also use:
- `shared/schemas/contract_fragment_ir.schema.yaml`
- `shared/schemas/negotiated_interface_ir.schema.yaml`
- `shared/schemas/adapter_contract.schema.yaml`
- `shared/schemas/protocol_monitor_contract.schema.yaml`
- `shared/schemas/noc_packet.schema.yaml`
- `shared/schemas/memory_queue_boundary.schema.yaml`
- `shared/schemas/structured_trace_table.schema.yaml`
- `shared/templates/memory_queue_boundary_report.md`

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.

### Source ID: `gpgpu-contract/packs/interconnect/address_mapping_evidence_contract.md`

# Address Mapping Evidence Contract

Address mapping evidence must include:

- physical address;
- partition/channel;
- L2 slice;
- bank;
- bank group when present;
- row and column when present;
- hashing/indexing policy provenance.

Bank skew and row locality claims require this evidence.

### Source ID: `gpgpu-contract/packs/interconnect/dram_scheduler_boundary_contract.md`

# DRAM Queue / Scheduler Boundary Contract

Interconnect may report DRAM-facing queue boundaries but must not define DRAM
scheduling truth.

Evidence passed to memory skill:

- L2-to-DRAM queue occupancy;
- request arrival order;
- DRAM queue enter/exit cycle;
- row/bank/channel address fields when available.

### Source ID: `gpgpu-contract/packs/interconnect/fabric_queue_backpressure_contract.md`

# Fabric Queue Backpressure Contract

Fabric backpressure is observable performance state and must not be hidden in
implementation-private queues.

## Queue Contract

```yaml
fabric_queue_backpressure:
  source_sm_id:
  queue_id:
  traffic_class:
  queue_occupancy:
  almost_full:
  arbitration_wait_cycles:
  virtual_channel:
  route_id:
```

## Rules

- Queue occupancy must be trace-visible for every route with backpressure.
- Atomic/fence queues must not be collapsed into ordinary load/store queues
  without an explicit synchronization contract.
- Missing backpressure evidence is `FABRIC_QUEUE_BACKPRESSURE_MISSING`.

### Source ID: `gpgpu-contract/packs/interconnect/fabric_request_response_contract.md`

# Fabric Request Response Contract

This file defines the request and response payload that leaves an SM and
returns from fabric, L2 cache slice, DRAM, atomic, or fence handling.

## Contract Fragment

`gpgpu-contract/packs/interconnect` emits this as `contract_fragment_ir` before
`gpgpu-contract` freezes `SYSTEM_CONTRACT_IR`.

```yaml
fabric_request:
  source_sm_id:
  source_warp_id:
  source_lane_mask:
  request_tag:
  traffic_class: load | store | atomic | fence | fill | writeback
  address:
  target_l2_slice_id:
  route_id:
  virtual_channel:
  ordering_scope:

fabric_response:
  source_request_tag:
  response_tag:
  source_sm_id:
  target_warp_id:
  target_lane_mask:
  final_eop:
  response_payload:
```

## Rules

1. Every request that leaves an SM must carry `source_sm_id`.
2. Every response must demux back to the original SM, warp, and lane shape.
3. Atomic and fence traffic must not be merged with ordinary load/store traffic
   unless `gpgpu-contract/packs/atomic_sync` explicitly permits the merge.
4. Fabric backpressure must expose queue occupancy trace.
5. Fabric route may affect performance and ordering, but must not change
   architectural semantics.

## Required Trace

- `l2_slice_route`
- `queue_occupancy`
- `fabric_route_id`
- `virtual_channel`
- `response_tag`
- `final_eop`

### Source ID: `gpgpu-contract/packs/interconnect/icnt_backpressure_contract.md`

# ICNT Buffer / Backpressure Contract

Backpressure evidence must distinguish:

- request path `has_buffer` failure;
- response path FIFO full;
- push blocked;
- pop blocked;
- packet volume by class;
- return-to-shader congestion.

Do not report only `NoC slow`.

### Source ID: `gpgpu-contract/packs/interconnect/l2_slice_routing_contract.md`

# L2 Slice Routing Contract

This file defines how an SM request selects an L2 cache slice or bypass memory
target. `L2 cache slice` is a hardware cache term, not a capability profile.

## SM to L2 routing table

```yaml
l2_slice_route:
  source_sm_id:
  request_tag:
  line_addr:
  target_l2_slice_id:
  route_id:
  arbitration policy:
  latency model:
  congestion model:
  memory request queue per SM:
```

## Rules

- The routing key must be deterministic and trace-visible.
- A route maps each SM to one or more L2 slices.
- Route choice must preserve response demux context.
- Route choice must not hide coherence, atomic, or fence ordering scope.

## Required Evidence

- `l2_slice_route_test`
- `response_demux_test`
- `multi_sm_trace_partition_test`

### Source ID: `gpgpu-contract/packs/interconnect/l2_subpartition_queue_contract.md`

# L2 Subpartition Queue Contract

L2/subpartition evidence must name:

- source SM;
- destination L2 slice/subpartition;
- request class;
- queue name;
- occupancy/capacity;
- hit/miss result;
- L2-to-DRAM queue event;
- return queue event.

### Source ID: `gpgpu-contract/packs/interconnect/noc_routing_contract.md`

# NoC Routing Contract

This contract defines `full_memory_sync_system` routing between SMs, L2 slices, and memory-system
targets.

## Required Routing State

Every route entry must include:
- source `sm_id`
- source queue ID
- destination L2 slice or memory target
- virtual channel or traffic class
- ordering scope
- arbitration class
- expected latency range
- congestion counter path

## SM to L2 routing table

SM to L2 routing table:
- maps each SM to one or more L2 slices
- defines address hashing or static slice selection
- records fallback route on slice backpressure
- preserves source SM for trace and attribution

## Arbitration Policy

arbitration policy must state:
- priority order
- fairness window
- starvation bound or explicit no-bound caveat
- handling for atomics and fences
- handling for writeback and read responses

## Latency Model

latency model must define:
- base route latency
- queue wait latency
- link traversal latency
- arbitration latency
- response return latency

## Congestion Model

congestion model must expose:
- input queue occupancy
- output queue occupancy
- dropped or retried request count
- link utilization
- arbitration wait cycles
- top blocked source SM

## Memory Request Queue Per SM

memory request queue per SM is required. The queue owns source ordering before
requests enter shared fabric arbitration.

Required fields:
- `sm_id`
- `request_sequence`
- `bundle_id`
- `memory_space`
- `ordering_scope`
- `queue_entry_state`
- `accepted_cycle`
- `dequeued_cycle`

## Failure Routing

Route failures:
- missing SM ID -> `gpgpu-rtl`
- ambiguous route -> `gpgpu-contract/packs/interconnect`
- incorrect memory visibility -> `gpgpu-contract/packs/memory_path`
- atomic/fence ordering mismatch -> `gpgpu-contract/packs/atomic_sync`

## XiangShan NoC Trace DB Hook

Interconnect routing must emit NoC packet and queue events into
`NOC_PACKET_LOG` or equivalent `STRUCTURED_TRACE_TABLE` with schema version,
config hash, source SM, target slice, virtual channel, route id, queue
occupancy, arbitration wait, and response tag. Every NoC trace feature must
ship a debug query and a performance attribution query.

### Source ID: `gpgpu-contract/packs/interconnect/packet_contract.md`

# Packet Contract

Packet fields:

- packet id;
- packet class;
- source;
- destination;
- request or response direction;
- byte size;
- flit count;
- VC class when used;
- `has_buffer` result;
- queue enter cycle;
- queue exit cycle.

NoC performance claims require packet class and size evidence.

### Source ID: `gpgpu-contract/packs/interconnect/response_demux_contract.md`

# Response Demux Contract

Responses from L2 cache slices, DRAM, atomics, or fabric must return to the
exact core-visible memory tag and lane shape that issued the request.

## Response Demux Payload

```yaml
response_demux:
  source_request_tag:
  response_tag:
  source_sm_id:
  target_warp_id:
  target_lane_mask:
  coalesced_tag:
  original_tag:
  restored_lane_mask:
  final_eop:
```

## Rules

- `source_sm_id` is mandatory on every response.
- `final_eop` gates scoreboard release and nonblocking tag release.
- Response demux must preserve atomic and fence response class.
- A demux mismatch is `RESPONSE_DEMUX_MISMATCH`.

### Source ID: `gpgpu-contract/packs/interconnect/return_path_contract.md`

# Return Path Contract

Return path evidence must distinguish:

- DRAM to L2 return;
- L2 to ICNT queue;
- ICNT to shader response;
- cluster or LSU response FIFO;
- scoreboard release.

Return congestion is not the same as request injection pressure.

### Source ID: `gpgpu-contract/packs/interconnect/sm_to_memory_fabric.md`

# SM To Memory Fabric

This contract defines how SM memory requests enter shared cache and DRAM
resources.

## Hierarchy

SM -> L1 -> L2 -> DRAM

Required hierarchy fields:
- `sm_id`
- `l1_instance_id`
- `l2_slice_id`
- `dram_channel_id`
- `request_class`
- `ordering_scope`
- `source_bundle_id`

## Request Merging Across SM

request merging across SM is allowed only when all merged requests have:
- compatible access type
- compatible address range
- compatible byte enables
- compatible memory ordering scope
- no atomic serialization conflict
- no fence drain dependency

Merged requests must retain source SM and warp contributor lists.

## L2 Cache Slicing Policy

L2 cache slicing policy must define:
- address-to-slice function
- source-SM override if present
- slice queue limits
- hit/miss trace fields
- response routing back to source SM

## Trace Contract

Every fabric trace event must include:
- source SM
- route path
- L1 result if modeled
- L2 slice result
- DRAM channel if accessed
- merge group ID if merged
- response target SM

## Acceptance

`full_memory_sync_system` interconnect passes only if:
- explicit NoC routing exists
- each request has a source SM
- merged requests preserve visibility and response routing
- fabric contention can be attributed to source SM and route segment
