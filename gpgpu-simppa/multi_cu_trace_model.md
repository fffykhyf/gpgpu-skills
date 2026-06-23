# Multi-CU Trace Model

This file defines trace partitioning for L3 multi-CU evidence and prepares the
system for L4 memory fabric attribution.

## CU-level trace partitioning

All normalized trace events must carry:
- `run_id`
- `cu_id`
- `wavefront_id`
- `event_order`
- `cycle` or logical order
- `pc`
- `event_type`
- `contract_path`
- `rtl_module_path`

CU-level trace partitioning means each CU can be compared independently before
global memory, atomic, or barrier ordering is evaluated.

## Wavefront interleaving model

wavefront interleaving model:
- events are ordered per wavefront
- issue events are ordered per CU
- memory requests are ordered per source CU and per memory ordering scope
- L2/DRAM/atomic events may create cross-CU order constraints

Trace normalization must not assume that lower event order in one CU precedes
an unrelated event in another CU.

## Memory ordering per CU

memory ordering per CU must record:
- source CU
- wavefront ID
- memory space
- request sequence number
- bundle ID
- response sequence number
- fence or atomic scope

Per-CU memory order is local unless a system contract declares global, acquire,
release, atomic, or barrier constraints.

## Multi-CU Independence

multi-CU independence is the default rule:
- local wavefront scheduling in CU A does not constrain local scheduling in CU B
- local LDS effects are visible only inside the owner CU
- global-memory visibility follows L4 memory/coherence contracts

## Attribution Buckets

L3/L4 attribution must distinguish:
- coalescing stall
- LDS stall
- inter-CU contention
- L2 queue wait
- DRAM bank conflict
- atomic serialization wait
- fence drain wait
- wave divergence attribution

## Human Dashboard

Human-facing validation dashboard should show:
- RTL vs golden verdict by CU
- top failing CU/wavefront
- first cross-CU ordering violation if present
- top memory-fabric bottleneck

Full per-event traces remain AI-facing artifacts.
