# Atomic Execution Model

This contract defines atomic ordering and visibility.

## Atomic Serialization Point

atomic serialization point must be exactly one of:
- L2 slice
- memory controller
- dedicated atomic unit
- explicitly unsupported trap path

The selected point must be recorded per memory scope.

## Per-SM Atomic Ordering

per-SM atomic ordering must define:
- source SM order
- warp order
- issue order
- serialization order
- response order
- visibility completion event

The model must state whether atomics from the same SM can pass non-atomic memory
operations and which fences prevent that.

## Global Atomic Consistency Model

global atomic consistency model must define:
- total order per address or per scope
- conflict granularity
- read-modify-write visibility
- interaction with cache coherence
- interaction with DRAM scheduling
- trace event that proves serialization

## Required Trace Fields

Atomic trace events must include:
- `sm_id`
- `warp_id`
- `pc`
- `address`
- `operation`
- `old_value`
- `new_value`
- `serialization_point`
- `serialization_sequence`
- `visibility_event`

## Acceptance

`full_memory_sync_system` atomic support passes only if:
- atomic ordering defined
- serialization point is explicit
- per-SM and global ordering are distinguishable
- cache/coherence visibility agrees with the atomic model
