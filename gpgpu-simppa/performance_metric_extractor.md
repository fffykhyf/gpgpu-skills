# Performance Metric Extractor

This component emits `PERFORMANCE_METRIC_IR` in both Failure Attribution Mode
and Pass Evidence Mode when cycle or ordered event evidence is available.

## Metric Groups

`correctness_smoke`:
- evidence completeness
- minimal fingerprint
- total cycles if available

`standard_validation`:
- basic IPC
- issue utilization
- stall breakdown
- memory latency summaries
- scheduler readiness summaries

`performance_gate`:
- full `PERFORMANCE_METRIC_IR`
- `PERF_ATTRIBUTION_GRAPH` even when correctness passes
- architecture rewrite trigger evaluation

## PERFORMANCE_METRIC_IR Shape

```yaml
performance_metric_ir:
  total_cycles: integer
  active_cycles: integer
  issue_cycles: integer
  commit_cycles: integer

  ipc: float
  warp_eligible_rate: float
  warp_issue_rate: float
  issue_utilization: float
  pipeline_utilization:
    fetch: float
    decode: float
    issue: float
    execute: float
    writeback: float
    memory: float

  stall_breakdown:
    scoreboard_dependency: integer
    no_ready_warp: integer
    memory_wait: integer
    lsq_full: integer
    coalescer_wait: integer
    bank_conflict: integer
    barrier_wait: integer
    divergence_reconvergence: integer
    register_file_port_conflict: integer
    pipeline_busy: integer
    interface_backpressure: integer
    runtime_wait: integer
    unknown: integer

  memory_metrics:
    global_memory_latency_avg: float
    global_memory_latency_p95: float
    shared_bank_conflict_rate: float
    coalescing_efficiency: float
    cache_hit_rate: optional float
    memory_replay_count: integer

  scheduler_metrics:
    ready_warp_count_avg: float
    eligible_warp_count_avg: float
    issued_warp_count: integer
    ready_but_not_issued_cycles: integer

  warning_flags:
    - LOW_ISSUE_UTILIZATION
    - HIGH_MEMORY_STALL
    - HIGH_BANK_CONFLICT
    - HIGH_INTERFACE_BACKPRESSURE
    - LOW_OCCUPANCY

  metric_groups:
    - scheduler
    - pipeline
    - memory_path
    - fabric
    - cache_mshr
    - dram
    - sync_atomic
```

## Backend PPA Evidence

Performance, FPGA, or power claims require an artifact bundle, not only a
passing simulation log.

```yaml
backend_perf_evidence:
  runtime_counter_dump: optional path
  simulator_perf_counter: optional path
  rtl_cycle_counter: optional path
  vcd_available: bool
  saif_available: bool
  synthesis_utilization_report: optional path
  timing_report: optional path
  power_report: optional path
  fpga_run_log: optional path
```

Warnings:

- `PPA_CLAIM_WITHOUT_SYNTHESIS_BUNDLE`
- `POWER_CLAIM_WITHOUT_SAIF`
- `FPGA_CLAIM_WITHOUT_BACKEND_RUN`
- `PERF_COUNTER_UNBOUND_TO_CONTRACT`

## Extraction Rules

- Use normalized event types and stall reason taxonomy only.
- If cycles are absent but order keys exist, emit ordered counts and mark rates
  as unavailable.
- Do not convert a metric warning into a root cause without bottleneck graph
  evidence.
- Preserve `performance_metric_hash` for regression fingerprinting.
- Reject PPA claims when `backend_perf_evidence` lacks the required backend
  matrix artifacts.
