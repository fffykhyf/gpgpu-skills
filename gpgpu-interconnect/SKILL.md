---
name: gpgpu-interconnect
description: Use when SM memory requests must be routed through NoC, L1/L2 fabric, cross-SM queues, congestion models, or SM-to-memory fabric contracts before DRAM, coherence, atomic, or fence behavior is evaluated.
---

# GPGPU Interconnect Contract Engine

## Role

This skill defines the `full_memory_sync_system` interconnect contract between SM-local memory
front-ends and the shared memory hierarchy. It owns NoC routing, SM-to-L2
mapping, request queues, fabric arbitration, and congestion evidence.

## Position in Flow

Upstream:
- `gpgpu-arch`
- `gpgpu-runtime`
- `gpgpu-rtl`

Downstream:
- `gpgpu-golden`
- `gpgpu-memory`
- `gpgpu-atomic-sync`
- `gpgpu-simppa`
- `gpgpu-loop`

## Input IR

Consumes:
- `ARCH_IR`
- `CAPABILITY_PROFILE_IR`
- `INCREMENTAL_RTL_MAP`
- `MEMORY_BUNDLE`
- per-SM trace partitions
- memory hierarchy constraints
- `shared/references/vortex_memory_sync_lessons.yaml`

## Output IR

Produces:
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

Required reference lessons:
- `VORTEX_CACHE_MSHR_RESPONSE_ROUTE`
- `VORTEX_SIMX_RTL_TWIN`

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
enter/exit cycles, and address mapping fields to `gpgpu-memory`.

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

## Required Tables

This skill must use:
- `shared/tables/output_mode_table.yaml`
- `shared/tables/artifact_visibility_table.yaml`
- `shared/tables/report_language_policy.yaml`
- `shared/tables/human_report_template_table.yaml`
- `shared/tables/revalidation_routing_table.yaml`
- `shared/tables/root_cause_taxonomy.yaml`
- `shared/tables/stall_reason_taxonomy.md`

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/incremental_rtl_map.schema.yaml`
- `shared/schemas/normalized_trace_ir.schema.yaml`
- `shared/schemas/noc_packet.schema.yaml`
- `shared/schemas/memory_queue_boundary.schema.yaml`
- `shared/schemas/memory_request_lifecycle.schema.yaml`

## Required Invariants

The output must satisfy:
- every memory request entering the fabric has a `sm_id`
- every route names source SM, destination L2 slice or memory target, arbitration class, and ordering scope
- request merging across SM is explicit and never changes memory visibility
- congestion evidence maps to links, queues, and source SMs
- NoC bottlenecks must state request/response packet volume, has-buffer failure, or return FIFO pressure.
- DRAM bottleneck claims must be handed off with row locality, bank skew, queue occupancy, or address mapping evidence rather than asserted generically.
- Request path and return path must remain separately attributable.
- interconnect artifacts preserve `ARTIFACT_MANIFEST_IR` provenance

## Failure Modes

This skill must emit:
- `NOC_ROUTE_MISSING`
- `SM_ID_ROUTE_MISSING`
- `FABRIC_ARBITRATION_AMBIGUOUS`
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
- sm_to_memory_fabric_hash
- route_results
- queue_results
- congestion_results
- affected_sm_ids
- downstream_contract

## Concrete Assets Required

This skill is incomplete unless the following exist:
- `noc_routing_contract.md`
- `sm_to_memory_fabric.md`
- `packet_contract.md`
- `icnt_backpressure_contract.md`
- `l2_subpartition_queue_contract.md`
- `dram_scheduler_boundary_contract.md`
- `address_mapping_evidence_contract.md`
- `return_path_contract.md`
- `shared/schemas/noc_packet.schema.yaml`
- `shared/schemas/memory_queue_boundary.schema.yaml`
- `shared/templates/memory_queue_boundary_report.md`

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
