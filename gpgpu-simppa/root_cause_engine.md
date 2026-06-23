# Root Cause Engine

The root cause engine classifies correctness and performance failures from
`FIRST_DIVERGENCE_REPORT`, `PERFORMANCE_METRIC_IR`, toolchain attribution, and
`PERF_ATTRIBUTION_GRAPH`.

## Root Cause Taxonomy

Top-level classes:

- `CONTRACT_ROOT_CAUSE`
- `GOLDEN_MODEL_ROOT_CAUSE`
- `TOOLCHAIN_ROOT_CAUSE`
- `RUNTIME_LAUNCH_ROOT_CAUSE`
- `RTL_FUNCTIONAL_ROOT_CAUSE`
- `RTL_INTERFACE_ROOT_CAUSE`
- `MEMORY_SYSTEM_ROOT_CAUSE`
- `SCHEDULER_ROOT_CAUSE`
- `PERFORMANCE_ARCH_ROOT_CAUSE`
- `TEST_EVIDENCE_ROOT_CAUSE`
- `INSUFFICIENT_TRACE_EVIDENCE`
- `ROOT_CAUSE_AMBIGUOUS`

Subclasses:

```yaml
TOOLCHAIN_ROOT_CAUSE:
  - ASM_PARSE_FAIL
  - ASM_ENCODE_MISMATCH
  - DISASM_ROUNDTRIP_MISMATCH
  - PROGRAM_IMAGE_LAYOUT_MISMATCH
  - ENTRY_SYMBOL_RESOLVE_MISMATCH
  - LOADER_CONTRACT_MISMATCH

RUNTIME_LAUNCH_ROOT_CAUSE:
  - ARG_BUFFER_ENCODING_MISMATCH
  - GRID_DIM_MISMATCH
  - BLOCK_DIM_MISMATCH
  - KERNEL_ENTRY_MISMATCH
  - CSR_START_SEQUENCE_MISMATCH
  - COMPLETION_OBSERVATION_MISMATCH

RTL_FUNCTIONAL_ROOT_CAUSE:
  - PC_UPDATE_MISMATCH
  - DECODE_MISMATCH
  - ACTIVE_MASK_MISMATCH
  - PREDICATE_MASK_MISMATCH
  - REGISTER_WRITEBACK_MISMATCH
  - BRANCH_DIVERGENCE_MISMATCH
  - BARRIER_STATE_MISMATCH

RTL_INTERFACE_ROOT_CAUSE:
  - VALID_READY_PROTOCOL_MISMATCH
  - PAYLOAD_STABILITY_VIOLATION
  - RESPONSE_TAG_MISMATCH
  - REQUEST_RESPONSE_ORDER_MISMATCH
  - BACKPRESSURE_DEADLOCK

MEMORY_SYSTEM_ROOT_CAUSE:
  - COALESCING_MISMATCH
  - COALESCER_RESPONSE_SHAPE_MISMATCH
  - COALESCER_TAG_RESTORE_MISMATCH
  - CACHE_REPLAY_ORDER_MISMATCH
  - MSHR_DEADLOCK_GUARD_MISSING
  - SCOREBOARD_WAKEUP_BEFORE_FINAL_RESPONSE
  - BYTE_ENABLE_MISMATCH
  - LANE_MASK_MISMATCH
  - LSQ_ORDERING_MISMATCH
  - DUPLICATE_REQUEST
  - RESPONSE_ROUTING_MISMATCH
  - BANK_CONFLICT_OVERHEAD
  - MEMORY_REPLAY_OVERHEAD

SCHEDULER_ROOT_CAUSE:
  - LOW_ELIGIBLE_WARP_RATE
  - SCOREBOARD_WAKEUP_DELAY
  - UNFAIR_WARP_SELECTION
  - READY_WARP_NOT_ISSUED
  - EXCESSIVE_BARRIER_WAIT

PERFORMANCE_ARCH_ROOT_CAUSE:
  - LOW_OCCUPANCY
  - PIPELINE_IMBALANCE
  - REGISTER_FILE_PORT_PRESSURE
  - MEMORY_BANDWIDTH_SATURATION
  - ISSUE_WIDTH_UNDERUTILIZATION
  - EXCESSIVE_DIVERGENCE_OVERHEAD

TEST_EVIDENCE_ROOT_CAUSE:
  - MISSING_GOLDEN_TRACE
  - MISSING_RTL_TRACE
  - HASH_MISMATCH
  - INSUFFICIENT_COVERAGE
  - AMBIGUOUS_TRACE_ORDERING
```

## Required Output

```yaml
root_cause_report:
  root_cause_class: string
  root_cause_subclass: string
  confidence: HIGH | MEDIUM | LOW
  minimal_trace_window: object
  first_divergence_ref: optional string
  performance_metric_ref: optional string
  contract_paths: list
  rtl_module_paths: list
  toolchain_artifact_paths: list
  evidence_hashes: list
  rewrite_candidate:
    patch_type: CONTRACT_PATCH | GOLDEN_MODEL_PATCH | TOOLCHAIN_PATCH | RUNTIME_PATCH | RTL_PATCH | ARCHITECTURE_PATCH | TEST_EVIDENCE_PATCH
    target_owner_skill: string
    required_revalidation: list
```

## Ranking Rules

- Prefer the earliest deterministic failure in the causal graph.
- Prefer toolchain or runtime root cause when assembler, program image, loader,
  launch, or first-fetch evidence fails before RTL decode evidence.
- Prefer RTL functional root cause when first divergence is PC, decode, active
  mask, predicate, register writeback, branch, or barrier state.
- Prefer RTL interface root cause when valid/ready, payload stability, response
  tag, ordering, or backpressure contract evidence fails.
- Prefer memory-system root cause when coalescer response restoration, cache
  replay order, MSHR almost-full gating, or final-response scoreboard wakeup
  evidence fails.
- Prefer performance architecture root cause only when correctness passes or
  correctness failure is unrelated and the bottleneck graph is complete.
- If multiple causes cannot be ranked from evidence, emit
  `ROOT_CAUSE_AMBIGUOUS`.
