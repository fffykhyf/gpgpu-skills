# Fence Visibility Contract

Fence is a memory visibility primitive, not a barrier.

```yaml
fence_visibility:
  fence_scope: warp | sm | device | system
  affected_memory_spaces:
  drain_begin_event:
  drain_end_event:
  pre_fence_write_set:
  post_fence_read_visibility:
  completion_condition:
```

Rules:

- Fence does not require all warps to arrive.
- Fence completion must be later than the required visibility event.
- `FENCE_DRAIN_INCOMPLETE` routes to `SYNC_ATOMIC_PATCH`.
