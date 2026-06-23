# Response Demux Contract

Responses from L2 cache slices, DRAM, atomics, or fabric must return to the
exact core-visible memory tag and lane shape that issued the request.

## Response Demux Payload

```yaml
response_demux:
  source_request_tag:
  response_tag:
  source_sm_id:
  target_warp_id:
  target_lane_mask:
  coalesced_tag:
  original_tag:
  restored_lane_mask:
  final_eop:
```

## Rules

- `source_sm_id` is mandatory on every response.
- `final_eop` gates scoreboard release and nonblocking tag release.
- Response demux must preserve atomic and fence response class.
- A demux mismatch is `RESPONSE_DEMUX_MISMATCH`.
