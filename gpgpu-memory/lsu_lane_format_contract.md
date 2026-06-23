# LSU Lane Format Contract

This contract is derived from the Vortex `VX_lsu_slice` lesson. The LSU
front-end must preserve lane shape before any cache, coalescer, or fabric step.

```yaml
lsu_lane_request:
  sm_id:
  warp_id:
  instruction_uuid:
  lane_mask:
  per_lane_addr:
  aligned_addr:
  access_size:
  byte_enable:
  store_data_shifted:
  memory_space: shared | global | constant | local
  load_format_rule: raw | sign_extend | zero_extend | nan_box
```

Acceptance requires traceable address alignment, byte enable, shifted store
data, load response formatting, and lane mask preservation.
