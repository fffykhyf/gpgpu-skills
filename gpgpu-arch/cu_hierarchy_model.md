# CU Hierarchy Model

This file defines the architecture hierarchy for the L3 CU-centric upgrade.
`CU` replaces `SM` as the canonical execution island in GPGPU skills.

## Hierarchy

```text
GPU
  -> CU array
      -> CU
          -> Wavepool
          -> Exec context table
          -> SIMD lanes
          -> SGPR bank
          -> VGPR bank
          -> LDS
          -> LSU
          -> Issue Arbiter
          -> Trace adapter
```

## CU is the canonical execution island

A CU is the smallest independently scheduled execution island. It owns the
resident wavefront resources and the local issue contract.

Required CU fields:
- `cu_id`
- `wavefront_slots`
- `wavefront_size_options`
- `issue_width`
- `simd_lane_count`
- `lds_capacity_bytes`
- `sgpr_bank_count`
- `vgpr_bank_count`
- `lsu_frontend_count`
- `memory_port_count`
- `trace_partition_id`

## Required Subsystems

### Wavepool

The wavepool stores resident wavefront identity, queued fetch/decode packets,
and per-wavefront resource bases.

Required state:
- resident wavefront bitmap
- dispatch tag map
- per-wavefront PC
- SGPR/VGPR/LDS base fields
- instruction queue occupancy
- queue reset causes

### Exec context table

The exec context table owns per-wavefront control and predicate state.

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
64-thread, or configurable wavefront widths.

### LDS

LDS is local to the CU unless the system contract explicitly defines a
different scope. LDS addresses must not be treated as a global-memory alias.

### LSU

The LSU front-end consumes decode-time memory bundles, computes per-lane
addresses, forms coalesced transactions, tags the memory space as global or
LDS, and reports completion back to issue state.

### Issue Arbiter

The Issue Arbiter selects ready wavefront work using an inspectable equation:
decoded valid, FU class, GPR readiness, special-state readiness, memory wait,
branch wait, barrier wait, max in-flight, and FU availability.

## Independence Rule

CU is fully independent execution island.

Required invariant:
- no shared execution state across CU
- no cross-CU dependency for wavefront residency, PC, EXEC, SGPR, VGPR, LDS, or issue readiness
- cross-CU interaction occurs only through defined memory, atomic, barrier, or system fabric contracts

## Multi-CU Routing

Multi-CU architecture must define:
- `cu_count`
- workgroup-to-CU dispatch mapping
- wavefront-to-CU residency rule
- CU_ID routing rule for traces and memory requests
- memory fabric request source ID
- per-CU performance counter partition

## Forbidden Architecture Defaults

The generator must not silently emit:
- `sm_count`
- `max_warps_per_sm`
- `warp_scheduler`
- `SM scheduler`
- generic `execution pipeline` as the top execution contract

Use:
- `cu_count`
- `wavefront_slots_per_cu`
- `wavefront_scheduler`
- `CU issue model`
- typed decode/issue/memory bundle contracts

## L3 Acceptance

A generated `ARCH_IR` reaches L3 only if:
- it uses CU instead of SM as the top execution island
- wavefront state includes explicit EXEC lifecycle
- LDS is local to CU and separately tagged from global memory
- coalescer policy is contract-defined
- multi-CU independence is enforced
