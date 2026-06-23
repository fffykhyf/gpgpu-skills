# DRAM Controller Contract

This contract defines `full_memory_sync_system` DRAM behavior visible to GPGPU correctness and
performance attribution.

## Memory Request Ordering

memory request ordering must define:
- source SM order
- address order
- read/write order
- fence drain order
- atomic order handoff
- response return order

The contract must distinguish required architectural order from performance
reordering that preserves visibility.

## Burst Scheduling

burst scheduling must define:
- burst size
- row-hit policy
- read/write turnaround policy
- queue selection policy
- starvation bound or explicit caveat
- trace fields for selected bank and row

## Bank-Level Parallelism Model

bank-level parallelism model must define:
- bank count
- bank address mapping
- row buffer state if modeled
- bank conflict detection
- concurrent bank access limits
- bank conflict stall attribution

## Trace Evidence

Required DRAM trace fields:
- request ID
- source SM
- L2 slice
- DRAM channel
- bank
- row
- burst length
- queue wait
- service cycles
- response ID

## Acceptance

`full_memory_sync_system` DRAM passes only if:
- DRAM controller contract defined
- memory request ordering is explicit
- bank-level parallelism model is present
- burst scheduling is auditable
- performance stalls can distinguish DRAM bank conflict from NoC/L2 contention
