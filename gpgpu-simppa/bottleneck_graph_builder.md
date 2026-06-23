# Bottleneck Graph Builder

The bottleneck graph builder converts normalized events and performance metrics
into `PERF_ATTRIBUTION_GRAPH`. It supports correctness failure graphs and
performance bottleneck graphs.

## Required Causal Chain

For a performance root cause or architecture rewrite recommendation, the graph
must connect:

```text
cycle_or_order_window
  -> warp_or_block_context
  -> bottleneck_or_divergence_event
  -> RTL module path or toolchain artifact path
  -> SYSTEM_CONTRACT_IR path
```

Memory-specific chains may still use:

```text
warp_stall
  -> scoreboard_dependency
  -> lsu_lane_format / memory_tag_allocate / coalescer_merge
  -> l1_cache_hit_or_miss / l2_slice_route / mshr_replay / dram_bank_conflict
  -> rtl_memory_or_fabric_module
  -> contract_rule
```

## Node Classes

- `cycle_window`
- `order_window`
- `block`
- `warp`
- `lane`
- `instruction`
- `pc_event`
- `decode_event`
- `active_mask_event`
- `register_writeback`
- `scoreboard_dependency`
- `scheduler_state`
- `barrier_state`
- `branch_divergence`
- `memory_request`
- `memory_response`
- `lsu_lane_format`
- `memory_tag`
- `cache_event`
- `l2_slice_route`
- `mshr_replay`
- `dram_schedule`
- `bank_conflict`
- `coalescing_event`
- `atomic_serialization`
- `fence_visibility`
- `barrier_phase`
- `wsync_drain`
- `interface_backpressure`
- `rtl_pipeline_stage`
- `toolchain_artifact`
- `runtime_launch_event`
- `contract_rule`
- `bottleneck_category`

## Edge Classes

- `caused_by`
- `blocked_by`
- `waits_for`
- `violates`
- `maps_to`
- `amplified_by`
- `precedes`
- `depends_on`
- `routes_to`

## Causal Templates

The builder is template-driven. Supported templates:

- `memory_latency_template`
- `shared_bank_conflict_template`
- `scoreboard_dependency_template`
- `scheduler_underutilization_template`
- `barrier_synchronization_template`
- `branch_divergence_template`
- `pipeline_imbalance_template`
- `interface_backpressure_template`
- `toolchain_mismatch_template`
- `runtime_launch_mismatch_template`
- `coalescer_restore_mismatch_template`
- `l2_slice_route_mismatch_template`
- `mshr_replay_mismatch_template`
- `atomic_serialization_mismatch_template`
- `fence_drain_incomplete_template`

Example:

```yaml
scheduler_underutilization_template:
  nodes:
    - cycle_window
    - low_eligible_warp_count
    - scoreboard_or_barrier_or_divergence
    - scheduler_policy
    - warp_scheduler_module
    - execution_model_scheduler_contract
  edges:
    - cycle_window blocked_by low_eligible_warp_count
    - low_eligible_warp_count caused_by scoreboard_or_barrier_or_divergence
    - scoreboard_or_barrier_or_divergence maps_to warp_scheduler_module
    - warp_scheduler_module maps_to execution_model_scheduler_contract
```

Toolchain example:

```yaml
assembler_encoding_mismatch_template:
  nodes:
    - instruction_mismatch
    - encoded_instruction
    - assembler_trace
    - isa_model_instruction_encoding
    - assembler_artifact
  edges:
    - instruction_mismatch caused_by encoded_instruction
    - encoded_instruction maps_to assembler_trace
    - assembler_trace maps_to isa_model_instruction_encoding
    - assembler_trace maps_to assembler_artifact
```

## Fail-Closed Rule

If the graph cannot connect event evidence, contract path, and RTL module path
or toolchain artifact path for the selected claim, the verdict is
`INSUFFICIENT_TRACE_EVIDENCE`.

## XiangShan TopDown GPGPU Attribution

`TOPDOWN_GPGPU_ATTRIBUTION` partitions total cycles into frontend/fetch/decode
idle, warp scheduling stall, scoreboard dependency stall, memory pipeline
stall, synchronization stall, tensor/ALU busy, and structural conflict. Memory
pipeline stall must be further attributable to coalescer, L1, MSHR, NoC, L2,
DRAM, or return path when those traces exist.
