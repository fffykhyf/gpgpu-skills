# Debug Attribution Pack

## Merged Source Material

### Source ID: `gpgpu-validation/differential_correctness_engine.md`

# Differential Correctness Engine

This component is required only in Failure Attribution Mode. It compares RTL,
golden, memory, CSR, fault, and completion evidence to find the earliest
deterministic architectural divergence.

## Compared Signals

- PC and next PC
- decoded instruction
- active mask and predicate mask
- register read values
- register writeback values
- memory request address, size, byte enable, lane mask, and tag
- memory response value, tag, and routing
- CSR update
- barrier state
- scoreboard state
- fault status
- completion status
- final memory dump

## Output

```yaml
first_divergence_report:
  verdict: DIVERGENCE_FOUND | NO_DIVERGENCE_FOUND | INSUFFICIENT_TRACE
  first_divergence_type: PC_MISMATCH | NEXT_PC_MISMATCH | DECODE_MISMATCH | ACTIVE_MASK_MISMATCH | PREDICATE_MASK_MISMATCH | REGISTER_WRITEBACK_MISMATCH | MEMORY_ADDRESS_MISMATCH | MEMORY_VALUE_MISMATCH | MEMORY_BYTE_ENABLE_MISMATCH | RESPONSE_TAG_MISMATCH | CSR_MISMATCH | BARRIER_STATE_MISMATCH | FAULT_STATUS_MISMATCH | COMPLETION_STATUS_MISMATCH
  cycle: optional integer
  step_id: optional integer
  warp_id: optional integer
  pc: optional string
  golden_event: object
  rtl_event: object
  contract_paths: list
  rtl_module_paths: list
  toolchain_artifact_paths: list
  precondition_window: list
  postcondition_window: list
  evidence_hashes: list
  confidence: HIGH | MEDIUM | LOW
```

## Ranking Rules

- Prefer the first deterministic architectural divergence.
- Do not report final memory mismatch as root cause. It is a symptom unless it
  is the first observable architectural divergence available.
- Prefer event pairs that share instruction identity, warp identity, and
  deterministic order.
- If PC, decode, active mask, and register evidence are all missing, emit
  `INSUFFICIENT_TRACE`.
- If toolchain evidence exists, compare assembler/program image/loader/runtime
  chain before blaming RTL fetch or decode.

## XiangShan Basic vs Full Diff

Use `XIANGSHAN_BASIC_AND_FULL_DIFF` as the diff layering rule:

- `BASIC_DIFF_TRACE` is always available and covers `WARP_INSTR_COMMIT`,
  `LANE_REG_WRITEBACK`, trap/fault, and launch completion events.
- `FULL_TRANSACTION_DIFF_TRACE` is debug-only and covers
  `MEMORY_TRANSACTION_EVENT`, `SYNC_SIDECHANNEL_EVENT`, coalescer/cache/MSHR,
  atomic/fence/barrier, control, abort, and debug halt events.

Every failure must emit `MISMATCH_PACKAGE` with first bad cycle, first bad event,
event type, expected value, actual value, suspected owner, required traces,
`REPLAY_WINDOW`, related config hash, and runtime image hash. Final output or
final memory mismatch is a symptom unless it is also the first bad event.

### Source ID: `gpgpu-validation/legacy_validation_and_trace_constraints.md`

# Legacy Validation and Trace Constraints

This reference migrates the useful constraints from the removed
`gpgpu-toolchain-runtime-validator`, the validation portions of `gpgpu-contract/packs/memory_path-subsystem`,
and the trace and RTL/golden comparison portions of
`gpgpu-implementation-validator`, plus the useful evidence behavior from legacy
`gpgpu-toolchain-runtime`, `gpgpu-contract/packs/memory_path-path`, `gpgpu-contract-sim`,
`gpgpu-rtl-simt-core`, and `gpgpu-causal-trace-analyzer`.

## Runtime Validation Evidence

Runtime evidence must be normalized into `NORMALIZED_TRACE_IR`. Useful migrated
checks include:

- frontend subset compile or parse smoke
- assembler smoke
- program image or hex load smoke
- kernel test application evidence
- launch argument encoding
- grid, block, and thread mapping
- queue and doorbell behavior
- CSR synchronization
- completion observation
- fault observation
- golden output comparison

These checks validate behavior against `GOLDEN_CONTRACT_MODEL`; they must not
define launch or memory truth themselves.

The final cross-run output for this engine is `SIM_PERF_ATTRIBUTION_REPORT`,
with supporting `CORRECTNESS_GATE_REPORT`, `PASS_EVIDENCE_REPORT`,
`PERF_ATTRIBUTION_GRAPH`, `ROOT_CAUSE_REPORT`, and normalized trace evidence.

Runtime validation must not infer scheduler policy, allocate warps absent from
the contract, optimize memory visibility, modify config defaults, or treat the
backend transport as the launch ABI.

## Memory Correctness Evidence

Memory validation must compare trace evidence against contract paths and RTL
module paths. It must cover the applicable subset of:

- request lifecycle
- address-space selection
- coalescing result
- lane mask and byte enable behavior
- load/store queue ordering
- duplicate-request prevention
- request replay policy
- shared-memory bank conflict behavior
- cache miss and global response behavior
- atomic and fence ordering
- fault propagation
- scoreboard wakeup
- stall and backpressure behavior
- memory dump comparison

Any memory conclusion without cycle, warp, memory event, contract path, and RTL
module evidence is insufficient.

## RTL and Golden Trace Comparison

The engine must preserve the old implementation-validator discipline:

- collect RTL simulation trace
- collect waveform-derived trace when available
- collect golden contract trace derived from `GOLDEN_CONTRACT_MODEL`
- normalize field names and time bases
- compare PC, active mask, register writes, memory transactions, CSR changes,
  completion, and faults
- report first divergence with minimal trace window

Trace comparison must identify both contract path and module path whenever the
data allows it. A mismatch without enough evidence becomes
`INSUFFICIENT_TRACE_EVIDENCE`, not a guessed root cause.

## Pass Evidence Compatibility

Legacy validation often treated `RTL == golden` as the end of the flow. In v5,
that behavior is explicitly downgraded to compatibility behavior. A correctness
pass must still produce pass evidence, trace coverage, performance metrics, and
a regression fingerprint. Missing evidence in a passing run becomes
`PASS_WITH_INSUFFICIENT_EVIDENCE` or `TEST_EVIDENCE_ROOT_CAUSE`, not silent
success.

## Causal Attribution Requirement

Performance and correctness reports must become a causal graph, not a flat
report. The graph should connect:

```text
cycle
  -> warp
  -> scoreboard or scheduler state
  -> memory request or SM issue model event
  -> cache miss, bank conflict, replay, dependency, or pipeline bubble
  -> RTL module path
  -> SYSTEM_CONTRACT_IR path
```

Root cause classes include contract violation, golden model issue, toolchain
issue, runtime launch issue, RTL functional issue, RTL interface issue, memory
system issue, scheduler issue, performance architecture issue, missing
evidence, and test-evidence drift.

The migrated causal trace analyzer rule is mandatory: metrics are not enough.
Every root cause must cite trace evidence, a failed gate, and a path to either
`SYSTEM_CONTRACT_IR` or `INCREMENTAL_RTL_MAP`. If multiple root causes cannot be
ranked deterministically, emit `ROOT_CAUSE_AMBIGUOUS`.

### Source ID: `gpgpu-validation/root_cause_engine.md`

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
- `MEMORY_PATH_ROOT_CAUSE`
- `FABRIC_ROOT_CAUSE`
- `CACHE_MSHR_ROOT_CAUSE`
- `DRAM_ROOT_CAUSE`
- `SYNC_ATOMIC_ROOT_CAUSE`
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

MEMORY_PATH_ROOT_CAUSE:
  - LSU_LANE_FORMAT_MISMATCH
  - MEMORY_TAG_REUSE_BEFORE_EOP
  - COALESCER_RESPONSE_SHAPE_MISMATCH
  - BYTE_ENABLE_RESTORE_MISMATCH

FABRIC_ROOT_CAUSE:
  - L2_SLICE_ROUTE_MISMATCH
  - RESPONSE_DEMUX_MISMATCH
  - FABRIC_QUEUE_BACKPRESSURE_MISSING

CACHE_MSHR_ROOT_CAUSE:
  - MSHR_REPLAY_MISMATCH
  - CACHE_RESPONSE_ROUTING_MISMATCH
  - MSHR_DEADLOCK_GUARD_MISSING

DRAM_ROOT_CAUSE:
  - DRAM_ORDERING_MISMATCH
  - DRAM_BANK_CONFLICT_MODEL_MISMATCH
  - DRAM_RESPONSE_ORDER_MISMATCH

SYNC_ATOMIC_ROOT_CAUSE:
  - ATOMIC_SERIALIZATION_MISMATCH
  - FENCE_DRAIN_INCOMPLETE
  - BARRIER_PHASE_MISMATCH
  - WSYNC_DRAIN_MISMATCH

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
- Prefer memory-path root cause when LSU lane format, nonblocking tag lifetime,
  coalescer restore, or byte-enable restoration evidence fails.
- Prefer fabric root cause when SM source identity, L2 slice route, response
  demux, virtual-channel, ordering-scope, or queue backpressure evidence fails.
- Prefer cache/MSHR root cause when replay order, response routing, MSHR
  almost-full gating, fill completion, or no-deadlock evidence fails.
- Prefer DRAM root cause when channel/bank/row scheduling, bank conflict, or
  response order evidence fails after cache/MSHR routing is correct.
- Prefer sync/atomic root cause when atomic serialization, fence visibility,
  barrier phase, or WSYNC prior-work drain evidence fails.
- Prefer performance architecture root cause only when correctness passes or
  correctness failure is unrelated and the bottleneck graph is complete.
- If multiple causes cannot be ranked from evidence, emit
  `ROOT_CAUSE_AMBIGUOUS`.

## XiangShan Failure Package Routing

When `FAILURE_CAPTURE_PACKAGE` exists, root-cause ranking must cite its
`MISMATCH_PACKAGE`, `REPLAY_WINDOW`, config hash, runtime image hash, and
available artifact list. Missing trace, waveform, state, store-log, or counter
artifacts route to `TEST_EVIDENCE_PATCH` unless an absent reason proves the
artifact is intentionally unavailable.

### Source ID: `gpgpu-validation/root_cause_evidence_rule.md`

# Root Cause Evidence Rule

Every root cause must include:

- symptom counter;
- exclusion counter;
- queue or stage owner;
- possible fix target;
- confidence;
- contract path or explicit evidence gap.

If any field is missing, emit `INSUFFICIENT_TRACE_EVIDENCE` or route to
`COUNTER_SCHEMA_PATCH` / `TEST_EVIDENCE_PATCH`.

### Source ID: `gpgpu-validation/toolchain_trace_attribution.md`

# Toolchain Trace Attribution

This component aligns attribution with
`gpgpu-toolchain-runtime`. It checks the chain from assembly to
RTL fetch/decode before blaming RTL decode or execution.

## Checked Chain

```text
assembly
  -> encoded bytes
  -> disassembly
  -> program image
  -> loader
  -> runtime launch
  -> RTL fetch/decode
```

## Distinctions

The attribution must distinguish:
- assembler parse failure
- assembler encoding mismatch
- disassembler roundtrip mismatch
- program image layout mismatch
- entry PC or symbol resolution mismatch
- loader initialization mismatch
- runtime arg buffer mismatch
- RTL fetch mismatch
- RTL decode mismatch
- golden decode mismatch

## Output

```yaml
toolchain_attribution_report:
  verdict: TOOLCHAIN_PASS | TOOLCHAIN_ROOT_CAUSE_FOUND | TOOLCHAIN_TRACE_INSUFFICIENT
  checked_chain:
    assembly_ir_hash: string
    assembler_output_hash: string
    disassembly_hash: string
    program_image_hash: string
    loader_contract_hash: string
    runtime_launch_hash: string
    rtl_first_fetch_hash: string
  failure_point: ASM_PARSE | ASM_ENCODE | DISASM_DECODE | ROUNDTRIP | PROGRAM_IMAGE_LAYOUT | ENTRY_SYMBOL_RESOLUTION | LOADER_INIT | RUNTIME_ARG_ENCODING | RTL_FETCH | RTL_DECODE
  related_contract_paths:
    - isa_model.instruction_encodings
    - launch_model.program_image_format
    - launch_model.argument_buffer_layout
    - launch_model.loader_contract
  related_artifacts:
    - generated_tool:assembler.py
    - generated_tool:disassembler.py
    - generated_tool:program_image.py
    - generated_tool:runtime_launch.py
    - generated_tool:loader.py
```

## Attribution Rules

- If assembler bytes mismatch ISA encoding truth, classify
  `TOOLCHAIN_ROOT_CAUSE/ASM_ENCODE_MISMATCH`.
- If disassembly does not roundtrip, classify
  `TOOLCHAIN_ROOT_CAUSE/DISASM_ROUNDTRIP_MISMATCH`.
- If image layout or entry PC mismatches loader contract, classify
  `TOOLCHAIN_ROOT_CAUSE/PROGRAM_IMAGE_LAYOUT_MISMATCH` or
  `ENTRY_SYMBOL_RESOLVE_MISMATCH`.
- If runtime launch config, arg buffer, CSR start, completion, or fault
  observation mismatches, classify `RUNTIME_LAUNCH_ROOT_CAUSE`.
- If toolchain chain passes and RTL first fetch/decode diverges, continue to
  RTL functional attribution.

## Structured Trace Query Artifacts

Toolchain and runtime traces that feed a trace database must register tables in
`TRACE_DB_MANIFEST`. Each table-producing feature must provide one
`SQL_DEBUG_QUERY` for failure investigation and one `SQL_PERF_QUERY` for
attribution. Query artifacts are AI-facing English evidence and should be
referenced by human reports only as summarized results.

### Source ID: `gpgpu-validation/warp_trace_diff.md`

# Warp Trace Diff

This file upgrades differential comparison from raw instruction trace diff to
warp state and EXEC-mask aware comparison.

## Diff Granularity

instruction trace diff is insufficient.

Required diff layers:
- toolchain / assembler / program image / loader diff
- runtime launch / first fetch PC diff
- PC diff
- decoded instruction record diff
- EXEC mask diff
- VCC/SCC special-state diff
- warp state diff
- divergence path diff
- memory bundle diff
- coalesced transaction diff
- side-effect event diff

## EXEC mask diff

EXEC mask diff must report:
- `sm_id`
- `warp_id`
- `pc`
- expected mask
- actual mask
- producer event
- consumer event
- affected lanes
- dependent instruction or memory bundle

## Warp state diff

warp state diff must compare:
- `ACTIVE`
- `PENDING`
- `STALLED`
- `WAITING_MEMORY`
- `DIVERGED`
- `RECONVERGING`
- `RETIRED`

The report must include owner module and release condition for the mismatched
state.

## Divergence path diff

divergence path diff must compare:
- branch condition source
- taken mask
- not-taken mask
- selected path order
- reconvergence stack entries
- restored PC
- restored EXEC mask

## First Divergence Rule

The first divergence must be the earliest deterministic architectural mismatch,
not the final memory dump symptom. Memory mismatches must route back to the
memory bundle, coalescer, LDS/global space tag, atomic/fence, or writeback event
that first diverged.

## Compare Order

Use this first-divergence order:

1. toolchain / assembler / program image / loader
2. runtime launch / first fetch PC
3. decode class
4. scheduler selected warp
5. active mask / predicate mask
6. commit / writeback
7. memory request
8. memory response
9. scoreboard release
10. stall / replay / performance attribution

## Required Outputs

AI-facing reports:
- `FIRST_DIVERGENCE_REPORT`
- `NORMALIZED_TRACE_IR`
- `ROOT_CAUSE_REPORT`
- `PERF_ATTRIBUTION_GRAPH`

Human-facing reports:
- `DEBUG_SUMMARY.zh.md`
- `PATCH_CARD.zh.md` through `gpgpu-loop`

## Failure Routing

Route:
- EXEC/mask mismatch -> `gpgpu-contract` or `gpgpu-rtl`
- memory bundle mismatch -> `gpgpu-toolchain-runtime` or `gpgpu-rtl`
- coalescing mismatch -> `gpgpu-toolchain-runtime`, `gpgpu-rtl`, or `gpgpu-contract/packs/memory_path`
- cross-SM ordering mismatch -> `gpgpu-contract/packs/interconnect`, `gpgpu-contract/packs/memory_path`, or `gpgpu-contract/packs/atomic_sync`

## XiangShan Diff Event Requirements

Warp trace diff must consume `WARP_INSTR_COMMIT` and `LANE_REG_WRITEBACK` as the
basic commit channel. If a warp mismatch depends on memory, barrier, fence, or
atomic side effects, the report must request `FULL_TRANSACTION_DIFF_TRACE`
instead of guessing from commit-only evidence.
