# Nonblocking Memory Tag Contract

Nonblocking memory tags are allocated resources. They are not released by raw
fabric responses; they release only after the final core-visible response EOP.

```yaml
nonblocking_memory_tag:
  allocated_on: accepted_load_or_atomic_request
  released_on: final_core_visible_response_eop
  tag_payload:
    - sm_id
    - warp_id
    - instruction_uuid
    - original_lane_mask
    - byte_enable_vector
    - scoreboard_destination
    - response_restore_context
```

Forbidden behavior:

- raw memory response releases scoreboard;
- response without `final_eop` releases tag;
- tag reuse before final core-visible response.
