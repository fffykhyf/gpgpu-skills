# NoC Routing Contract

This contract defines `full_memory_sync_system` routing between SMs, L2 slices, and memory-system
targets.

## Required Routing State

Every route entry must include:
- source `sm_id`
- source queue ID
- destination L2 slice or memory target
- virtual channel or traffic class
- ordering scope
- arbitration class
- expected latency range
- congestion counter path

## SM to L2 routing table

SM to L2 routing table:
- maps each SM to one or more L2 slices
- defines address hashing or static slice selection
- records fallback route on slice backpressure
- preserves source SM for trace and attribution

## Arbitration Policy

arbitration policy must state:
- priority order
- fairness window
- starvation bound or explicit no-bound caveat
- handling for atomics and fences
- handling for writeback and read responses

## Latency Model

latency model must define:
- base route latency
- queue wait latency
- link traversal latency
- arbitration latency
- response return latency

## Congestion Model

congestion model must expose:
- input queue occupancy
- output queue occupancy
- dropped or retried request count
- link utilization
- arbitration wait cycles
- top blocked source SM

## Memory Request Queue Per SM

memory request queue per SM is required. The queue owns source ordering before
requests enter shared fabric arbitration.

Required fields:
- `sm_id`
- `request_sequence`
- `bundle_id`
- `memory_space`
- `ordering_scope`
- `queue_entry_state`
- `accepted_cycle`
- `dequeued_cycle`

## Failure Routing

Route failures:
- missing SM ID -> `gpgpu-rtl`
- ambiguous route -> `gpgpu-interconnect`
- incorrect memory visibility -> `gpgpu-memory`
- atomic/fence ordering mismatch -> `gpgpu-atomic-sync`
