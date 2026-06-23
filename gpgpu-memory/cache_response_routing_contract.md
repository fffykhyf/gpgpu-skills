# Cache Response Routing Contract

Cache response routing is responsible for returning fills, hits, replays,
writebacks, atomics, and bypass responses to the original core-visible request.

```yaml
cache_response_routing:
  source_sm_id:
  source_warp_id:
  source_request_tag:
  response_tag:
  l2_slice_id:
  cache_bank_id:
  mshr_id:
  restored_lane_mask:
  final_eop:
```

Failure modes:

- `CACHE_RESPONSE_ROUTING_MISMATCH`
- `RESPONSE_DEMUX_MISMATCH`
- `MEMORY_TAG_REUSE_BEFORE_EOP`
