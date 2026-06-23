# WSYNC Drain Contract

WSYNC is prior-work drain, not a normal scoreboard wakeup.

```yaml
wsync_drain:
  sm_id:
  warp_id:
  prior_work_count:
  pending_memory_ops:
  pending_long_latency_ops:
  drain_begin:
  drain_end:
  release_event:
```

Failure modes:

- `WSYNC_CLASSIFIED_AS_SCOREBOARD_HAZARD`
- `WSYNC_RELEASE_BEFORE_PRIOR_WORK_DRAIN`
- `BARRIER_RELEASE_WITHOUT_LSU_DRAIN`
- `FENCE_COMPLETES_BEFORE_VISIBILITY`
