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
