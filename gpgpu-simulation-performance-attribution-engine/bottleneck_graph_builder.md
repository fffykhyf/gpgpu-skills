# Bottleneck Graph Builder

The bottleneck graph builder converts normalized events into `PERF_ATTRIBUTION_GRAPH`.

## Required Causal Chain

```text
warp_stall
  -> scoreboard_dependency
  -> memory_request
  -> cache_miss / bank_conflict / ordering_wait
  -> rtl_pipeline_stage
  -> contract_rule
```

## Node Classes

- `cycle_window`
- `warp`
- `instruction`
- `scoreboard_dependency`
- `memory_request`
- `cache_event`
- `bank_conflict`
- `rtl_pipeline_stage`
- `contract_rule`
- `bottleneck_category`

## Edge Classes

- `caused_by`
- `blocked_by`
- `waits_for`
- `violates`
- `maps_to`
- `amplified_by`

If the graph cannot connect cycle, warp, memory, contract path, and RTL module evidence, the verdict is `INSUFFICIENT_TRACE_EVIDENCE`.
