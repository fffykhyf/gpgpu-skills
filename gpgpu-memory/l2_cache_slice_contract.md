# L2 Cache Slice Contract

`L2 cache slice` is a hardware cache component used by
`full_memory_sync_system`.

```yaml
l2_cache_slice:
  l2_slice_id:
  bank_id:
  line_addr:
  cache_tag:
  mshr_id:
  request_queue_occupancy:
  response_queue_occupancy:
  replay_policy:
  fill_policy:
  writeback_policy:
  response_demux_target:
```

The slice must preserve source SM, source warp, request tag, lane mask, and byte
enable through miss, fill, replay, and response demux.
