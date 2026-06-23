# Coalescer Response Restore Contract

coalescer correctness = request merge correctness + response restore correctness

```yaml
coalescer_merge:
  original_requests:
    - original_tag
    - lane_mask
    - per_lane_addr
    - per_lane_offset
    - byte_enable
  coalesced_request:
    coalesced_tag
    line_addr
    merged_byte_enable
    merged_lane_mask

coalescer_restore:
  coalesced_tag:
  original_tag:
  restored_lane_mask:
  restored_lane_data:
  final_eop:
```

Failure modes:

- `COALESCER_MERGE_UNSAFE`
- `COALESCER_RESPONSE_SHAPE_MISMATCH`
- `COALESCER_TAG_REUSE_BEFORE_EOP`
- `COALESCER_BYTE_ENABLE_RESTORE_MISMATCH`
