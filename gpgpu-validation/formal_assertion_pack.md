# Formal Assertion Pack

RTL correctness cannot be marked strong unless relevant assertion pack entries
are proven, bounded-checked, simulated as assertions, or explicitly waived with
a contract-path-bound reason.

## Valid / Ready Protocol

- `payload_stable_while_valid_not_ready`
- `no_accept_without_valid_and_ready`
- `no_drop_under_backpressure`
- `no_combinational_ready_loop`

## Scoreboard

- `scoreboard_reserve_before_issue`
- `scoreboard_release_requires_final_writeback`
- `scoreboard_no_duplicate_pending_tag`
- `scoreboard_hazard_blocks_issue`

## Memory Tag / Response

- `memory_tag_unique_until_response`
- `response_tag_matches_inflight_request`
- `response_restores_warp_lane_mask`
- `no_response_without_request`

## Coalescer

- `coalescer_preserves_original_lane_offsets`
- `coalescer_restore_exact_lane_mask`
- `coalescer_no_lane_data_cross_contamination`

## SIMT / Active Mask

- `inactive_lane_no_writeback`
- `branch_updates_exec_mask_contract`
- `join_restores_reconvergence_mask`

## Barrier / Fence / Atomic

- `barrier_releases_after_all_expected_warps`
- `fence_completion_requires_visibility_point`
- `atomic_serialization_point_unique`
- `wsync_drains_prior_work`

## Deterministic Assertion Naming

Assertion names must use:

```text
assert_<module_name>_<property_name>
```

Examples:

```text
assert_lsu_memory_tag_unique_until_response
assert_scoreboard_release_requires_final_writeback
assert_coalescer_restore_exact_lane_mask
```

Each assertion manifest entry must bind to a `SYSTEM_CONTRACT_IR` path and state
whether evidence is `proven`, `bounded_checked`, `simulated_assertion`, or
`waived_with_contract_reason`.
