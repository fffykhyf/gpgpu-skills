# SM Hierarchy Model

This file defines the architecture hierarchy for the SM-centric capability
profiles.
`SM` is the canonical execution island in GPGPU skills.

## Hierarchy

```text
GPU
  -> SM array
      -> SM
          -> Warp pool
          -> Exec context table
          -> SIMD lanes
          -> SGPR bank
          -> VGPR bank
          -> LDS
          -> LSU
          -> Issue Arbiter
          -> Trace adapter
```

## SM is the canonical execution island

A SM is the smallest independently scheduled execution island. It owns the
resident warp resources and the local issue contract.

Required SM fields:
- `sm_id`
- `warp_slots`
- `warp_size_options`
- `issue_width`
- `simd_lane_count`
- `lds_capacity_bytes`
- `sgpr_bank_count`
- `vgpr_bank_count`
- `lsu_frontend_count`
- `memory_port_count`
- `trace_partition_id`

## Required Subsystems

### Warp pool

The warp pool stores resident warp identity, queued fetch/decode packets,
and per-warp resource bases.

Required state:
- resident warp bitmap
- dispatch tag map
- per-warp PC
- SGPR/VGPR/LDS base fields
- instruction queue occupancy
- queue reset causes

### Exec context table

The exec context table owns per-warp control and predicate state.

Required state:
- EXEC mask
- VCC
- SCC
- M0 or target-specific special state
- pending branch bit
- barrier/wait state
- reconvergence stack pointer when enabled

### SIMD lanes

SIMD lanes execute vector operations under EXEC-mask driven gating. The
architecture contract must define whether the design supports 32-thread,
64-thread, or configurable warp widths.

### LDS

LDS is local to the SM unless the system contract explicitly defines a
different scope. LDS addresses must not be treated as a global-memory alias.

### LSU

The LSU front-end consumes decode-time memory bundles, computes per-lane
addresses, forms coalesced transactions, tags the memory space as global or
LDS, and reports completion back to issue state.

### Issue Arbiter

The Issue Arbiter selects ready warp work using an inspectable equation:
decoded valid, FU class, GPR readiness, special-state readiness, memory wait,
branch wait, barrier wait, max in-flight, and FU availability.

## Independence Rule

SM is fully independent execution island.

Required invariant:
- no shared execution state across SM
- no cross-SM dependency for warp residency, PC, EXEC, SGPR, VGPR, LDS, or issue readiness
- cross-SM interaction occurs only through defined memory, atomic, barrier, or system fabric contracts

## Multi-SM Routing

Multi-SM architecture must define:
- `sm_count`
- workgroup-to-SM dispatch mapping
- warp-to-SM residency rule
- SM_ID routing rule for traces and memory requests
- memory fabric request source ID
- per-SM performance counter partition

## Forbidden Architecture Defaults

The generator must not silently emit:
- `sm_count`
- `max_warps_per_sm`
- `warp_scheduler`
- `SM scheduler`
- generic `execution pipeline` as the top execution contract

Use:
- `sm_count`
- `warp_slots_per_sm`
- `warp_scheduler`
- `SM issue model`
- typed decode/issue/memory bundle contracts

## Capability Acceptance

A generated `ARCH_IR` reaches `single_sm_warp_pipeline` or
`multi_sm_memory_path` only if:
- it declares SM as the top execution island
- warp state includes explicit EXEC lifecycle
- LDS is local to SM and separately tagged from global memory
- coalescer policy is contract-defined
- multi-SM independence is enforced
