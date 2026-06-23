# MSHR Replay Contract

```yaml
mshr_replay_contract:
  allocate_on: cache_miss
  hold_context:
    - source_sm_id
    - source_warp_id
    - source_request_tag
    - line_addr
    - byte_enable
    - lane_mask
  replay_order_policy:
  fill_completion_event:
  release_event:

mshr_deadlock_guard:
  block_new_request_if:
    - mshr_almost_full
    - memory_request_queue_almost_full
    - response_queue_almost_full
    - writeback_egress_blocked
    - replay_queue_blocked
```

`MSHR_REPLAY_MISMATCH` routes to `MEMORY_PATH_PATCH`.
