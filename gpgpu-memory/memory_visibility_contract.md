# Memory Visibility Contract

Memory visibility is a correctness contract, not a cache implementation detail.

```yaml
memory_visibility:
  visibility_event:
  visibility_scope: warp | sm | device | system
  affected_memory_spaces:
  producer_event:
  consumer_event:
  ordering_scope:
  required_drain_events:
```

Rules:

- Fence visibility is owned jointly with `gpgpu-atomic-sync`.
- Barrier release does not imply memory visibility unless the contract says so.
- Atomic visibility and fence visibility are separate events.
