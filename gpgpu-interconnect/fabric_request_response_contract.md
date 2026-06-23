# Fabric Request Response Contract

This file defines the request and response payload that leaves an SM and
returns from fabric, L2 cache slice, DRAM, atomic, or fence handling.

## Contract Fragment

`gpgpu-interconnect` emits this as `contract_fragment_ir` before
`gpgpu-golden` freezes `SYSTEM_CONTRACT_IR`.

```yaml
fabric_request:
  source_sm_id:
  source_warp_id:
  source_lane_mask:
  request_tag:
  traffic_class: load | store | atomic | fence | fill | writeback
  address:
  target_l2_slice_id:
  route_id:
  virtual_channel:
  ordering_scope:

fabric_response:
  source_request_tag:
  response_tag:
  source_sm_id:
  target_warp_id:
  target_lane_mask:
  final_eop:
  response_payload:
```

## Rules

1. Every request that leaves an SM must carry `source_sm_id`.
2. Every response must demux back to the original SM, warp, and lane shape.
3. Atomic and fence traffic must not be merged with ordinary load/store traffic
   unless `gpgpu-atomic-sync` explicitly permits the merge.
4. Fabric backpressure must expose queue occupancy trace.
5. Fabric route may affect performance and ordering, but must not change
   architectural semantics.

## Required Trace

- `l2_slice_route`
- `queue_occupancy`
- `fabric_route_id`
- `virtual_channel`
- `response_tag`
- `final_eop`
