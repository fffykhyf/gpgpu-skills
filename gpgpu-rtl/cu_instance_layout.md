# CU Instance Layout

This file defines the RTL instance layout for a CU-centric GPGPU skill system.

## CU contains

CU contains:
- N SIMD lanes
- Wavepool (resident wave slots)
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
| `cu_top` | Owns CU boundary, CU_ID, reset, and submodule wiring. |
| `wavepool` | Owns resident slots, PC/base state, instruction queue, stop-fetch. |
| `wavefront_scheduler` | Selects a wavefront candidate and exposes readiness terms. |
| `cu_issue_arbiter` | Selects one or more issue records from ready candidates. |
| `decode_issue_table` | Stores typed decoded records per wavefront. |
| `exec_state` | Owns EXEC, VCC, SCC, and special-state files. |
| `simd_lane_cluster` | Executes vector operations under EXEC-mask gating. |
| `sgpr_bank` | Owns scalar RF storage and writeback merge. |
| `vgpr_bank` | Owns vector RF storage and lane-mask writes. |
| `lsu_frontend` | Consumes `MEMORY_BUNDLE` and emits memory-space tagged requests. |
| `lds_sram` | Implements CU-local LDS storage and bank-conflict reporting. |
| `trace_adapter` | Emits CU and wavefront partitioned side-effect events. |

## CU_ID routing rule

Every request, response, trace event, and performance event that can cross a CU
boundary must carry `cu_id` or a derived source ID.

Required carriers:
- dispatch packet
- instruction fetch request when shared frontend exists
- memory bundle
- L1/L2/DRAM request
- atomic request
- barrier/fence event
- trace event
- performance counter sample

## Wave dispatch mapping

Required phrase: wave dispatch mapping.

Dispatch maps workgroups and wavefronts to CUs by an explicit rule:
- static round-robin
- occupancy-aware
- runtime-provided CU assignment
- debug-fixed CU assignment

The mapping must be recorded in the launch/runtime artifact or contract. The
RTL binding must not infer wavefront placement from trace ordering.

## No cross-CU dependency

Required invariant:
- no cross-CU dependency for local wavefront scheduler readiness
- no direct read of another CU's SGPR/VGPR/EXEC/LDS state
- no shared branch, barrier, or scoreboard table across CUs

Allowed cross-CU interactions:
- global memory fabric
- L2/DRAM ordering
- atomics at the declared serialization point
- grid-level barriers through a system synchronization contract

## Binding Checks

The RTL binding must fail if:
- a module still exposes `sm_core` as the canonical top-level execution island
- `warp_scheduler` is used where `wavefront_scheduler` is required
- memory requests lack CU_ID routing
- LDS is bound as a global-memory alias
- a single global scoreboard owns multiple CU readiness states
