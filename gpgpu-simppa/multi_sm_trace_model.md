# Multi-SM Trace Model

This file defines trace partitioning for `multi_sm_memory_path` evidence and
prepares the system for `full_memory_sync_system` memory fabric attribution.

## SM-level trace partitioning

All normalized trace events must carry:
- `run_id`
- `sm_id`
- `warp_id`
- `event_order`
- `cycle` or logical order
- `pc`
- `event_type`
- `contract_path`
- `rtl_module_path`

SM-level trace partitioning means each SM can be compared independently before
global memory, atomic, or barrier ordering is evaluated.

## Warp interleaving model

warp interleaving model:
- events are ordered per warp
- issue events are ordered per SM
- memory requests are ordered per source SM and per memory ordering scope
- L2/DRAM/atomic events may create cross-SM order constraints

Trace normalization must not assume that lower event order in one SM precedes
an unrelated event in another SM.

## Memory ordering per SM

memory ordering per SM must record:
- source SM
- warp ID
- memory space
- request sequence number
- bundle ID
- response sequence number
- fence or atomic scope

Per-SM memory order is local unless a system contract declares global, acquire,
release, atomic, or barrier constraints.

## Multi-SM Independence

multi-SM independence is the default rule:
- local warp scheduling in SM A does not constrain local scheduling in SM B
- local LDS effects are visible only inside the owner SM
- global-memory visibility follows `full_memory_sync_system` memory/coherence contracts

## Attribution Buckets

Advanced memory-path and synchronization attribution must distinguish:
- coalescing stall
- LDS stall
- inter-SM contention
- L2 queue wait
- DRAM bank conflict
- atomic serialization wait
- fence drain wait
- wave divergence attribution

## Human Dashboard

Human-facing validation dashboard should show:
- RTL vs golden verdict by SM
- top failing SM/warp
- first cross-SM ordering violation if present
- top memory-fabric bottleneck

Full per-event traces remain AI-facing artifacts.
