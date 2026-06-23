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

Human-facing report:
- interconnect section in `VALIDATION_DASHBOARD.zh.md`

AI-facing artifacts:
- English `NOC_ROUTING_CONTRACT.yaml`
- English `SM_TO_MEMORY_FABRIC_IR.yaml`
- English `FABRIC_CONTENTION_REPORT.yaml`
- English `MEMORY_REQUEST_QUEUE_REPORT.yaml`

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

Required reference lessons:
- `VORTEX_CACHE_MSHR_RESPONSE_ROUTE`
- `VORTEX_SIMX_RTL_TWIN`

## Human and AI Output Policy

NoC and fabric contracts are AI-facing English artifacts. Human-facing output is
limited to Chinese dashboard status: routing verdict, top congested link,
affected SM IDs, request merging status, and required revalidation.

All full routing tables and queue traces must be registered in
`ARTIFACT_MANIFEST_IR`.

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

## Required Schemas

This skill must validate:
- `shared/schemas/output_mode_ir.schema.yaml`
- `shared/schemas/artifact_manifest_ir.schema.yaml`
- `shared/schemas/human_report_manifest_ir.schema.yaml`
- `shared/schemas/artifact_visibility_ir.schema.yaml`
- `shared/schemas/system_contract_ir.schema.yaml`
- `shared/schemas/incremental_rtl_map.schema.yaml`
- `shared/schemas/normalized_trace_ir.schema.yaml`

## Required Invariants

The output must satisfy:
- every memory request entering the fabric has a `sm_id`
- every route names source SM, destination L2 slice or memory target, arbitration class, and ordering scope
- request merging across SM is explicit and never changes memory visibility
- congestion evidence maps to links, queues, and source SMs
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

When a required schema, table, example, or test is missing, emit
`INSUFFICIENT_SKILL_ASSET` rather than inventing behavior.
