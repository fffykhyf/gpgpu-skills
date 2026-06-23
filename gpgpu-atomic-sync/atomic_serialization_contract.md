# Atomic Serialization Contract

Atomic behavior is separate from ordinary load/store coalescing and separate
from fence visibility.

```yaml
atomic_execution:
  operation:
  address:
  serialization_point:
  serialization_sequence:
  old_value:
  new_value:
  visibility_event:
  response_to_warp:
```

Rules:

- Atomic traffic must not be coalesced with ordinary load/store traffic unless
  this contract explicitly permits it.
- Atomic operation must name a serialization point.
- Atomic response must return to the original warp and lane.
- Atomic visibility and fence visibility are different events.
