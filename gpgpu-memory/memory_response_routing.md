# Memory Response Routing

Every memory response must preserve the identity needed to wake exactly the
original requester.

Required route:

- cache bank tag -> wrapper tag -> original request tag
- SM / warp / lane identity preservation
- final response release to scoreboard
- fault response routing to completion/fault observation

Required response fields:

- `response_tag`
- `original_request_tag`
- `sm_id`
- `warp_id`
- `lane_mask`
- `byte_enable`
- `per_lane_offset`
- `restored_lane_data`
- `final_eop`
- `scoreboard_release_event`

Failure modes:

- `RESPONSE_ROUTING_MISMATCH`
- `TAG_REUSE_BEFORE_RESPONSE`
- `SCOREBOARD_WAKEUP_BEFORE_FINAL_RESPONSE`
- `COALESCER_RESPONSE_SHAPE_MISMATCH`
