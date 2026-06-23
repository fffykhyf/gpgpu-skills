# Atomic Execution Model

This contract defines atomic ordering and visibility.

## Atomic Serialization Point

atomic serialization point must be exactly one of:
- L2 slice
- memory controller
- dedicated atomic unit
- explicitly unsupported trap path

The selected point must be recorded per memory scope.

## Per-CU Atomic Ordering

per-CU atomic ordering must define:
- source CU order
- wavefront order
- issue order
- serialization order
- response order
- visibility completion event

The model must state whether atomics from the same CU can pass non-atomic memory
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
- `cu_id`
- `wavefront_id`
- `pc`
- `address`
- `operation`
- `old_value`
- `new_value`
- `serialization_point`
- `serialization_sequence`
- `visibility_event`

## Acceptance

L4 atomic support passes only if:
- atomic ordering defined
- serialization point is explicit
- per-CU and global ordering are distinguishable
- cache/coherence visibility agrees with the atomic model
