# L2 Slice Routing Contract

This file defines how an SM request selects an L2 cache slice or bypass memory
target. `L2 cache slice` is a hardware cache term, not a capability profile.

## SM to L2 routing table

```yaml
l2_slice_route:
  source_sm_id:
  request_tag:
  line_addr:
  target_l2_slice_id:
  route_id:
  arbitration policy:
  latency model:
  congestion model:
  memory request queue per SM:
```

## Rules

- The routing key must be deterministic and trace-visible.
- A route maps each SM to one or more L2 slices.
- Route choice must preserve response demux context.
- Route choice must not hide coherence, atomic, or fence ordering scope.

## Required Evidence

- `l2_slice_route_test`
- `response_demux_test`
- `multi_sm_trace_partition_test`
