# xiangshan Source Summary

Distilled active summary from archived reference notes.

## README

# XiangShan Reference Library for GPGPU Skills

XiangShan is used as a hardware development-loop reference, not as a CPU
microarchitecture template. The transferable mechanisms are executable golden
reference APIs, layered differential tracing, replayable failure capture, safe
runtime design-space exploration, structured trace databases, and weighted
checkpoint-based performance attribution.

Default skill execution should read `shared/references/xiangshan_lessons.yaml`
and the concise lesson summaries in this directory. Raw reader reports under
`raw/` are lazy-load material for deep investigation only.

## Applies As

- golden reference closure pattern
- trace diff and first-divergence pattern
- bounded failure capture and replay pattern
- runtime-tunable DSE safety pattern
- structured trace DB and query pattern
- representative checkpoint and weighted performance pattern

## Does Not Apply As

- CPU frontend design reference
- branch predictor reference
- rename / ROB reference
- RISC-V privilege or CSR semantics reference
- scalar pipeline template
- XiangShan cache structure template

## difftest_trace_diff_lessons

# DiffTest Trace Diff Lessons

XiangShan DiffTest teaches that correctness evidence should be layered.
Always-on probes remain small, while full transaction probes are enabled for
debugging and failure localization.

GPGPU abstraction:

- `BASIC_DIFF_TRACE` is always available and covers warp commit, lane
  writeback, trap/fault, and launch completion.
- `FULL_TRANSACTION_DIFF_TRACE` is debug-only and covers memory, coalescer,
  cache/MSHR, sync, atomic, fence, control, and debug transactions.
- `MISMATCH_PACKAGE` records first bad cycle, first bad event, expected/actual,
  suspected owner, required traces, replay window, config, and runtime image.

Rule: final memory equality is not enough. The diff engine must localize the
first divergence event and classify it by owner domain.

## do_not_copy

# XiangShan Material Not To Copy

Do not migrate XiangShan CPU microarchitecture into GPGPU skills.

Forbidden transfers:

- CPU frontend, fetch queue, branch predictor, FTQ, RAS, TAGE, SC, or uBTB structure
- rename, ROB, scalar commit, CPU issue queue, or scalar pipeline semantics
- RISC-V privilege, exception, interrupt, PMP/PMA, CSR, CLINT, PLIC, or debug-module details
- XiangShan-specific cache hierarchy internals as mandatory GPGPU cache structure
- XiangShan workload assumptions as GPGPU workload defaults

Allowed transfer:

- development closure mechanics that keep RTL, golden reference, traces,
  replay, counters, and performance evidence synchronized.

## failure_capture_lessons

# Failure Capture Lessons

XiangShan LightSSS/XSPdb teaches that simulation failures should produce a
bounded replayable failure scene instead of full-run wave dumps.

GPGPU abstraction:

- `BATCH_AUTO_CAPTURE` is CI/regression mode for diff fail, assertion fail,
  timeout, and deadlock triggers.
- `INTERACTIVE_REPLAY_SESSION` is human-debug mode with step, break, dump, and
  compare commands.
- `FAILURE_CAPTURE_PACKAGE` contains replay command, trace slice, waveform
  slice or absent reason, config hash, program image hash, golden state, RTL
  state summary, memory store log, counter snapshot, and normalized report.
- `REPLAY_WINDOW` defines pre-failure and post-failure bounds.
- `DEBUG_TRIGGER` describes what caused capture and which context was required.

Rule: if an artifact is missing, the package must record an absent reason.

## golden_model_lessons

# Golden Model Lessons

XiangShan/NEMU teaches that a golden model should be a live executable
reference machine, not only an end-result checker.

GPGPU abstraction:

- `GOLDEN_REF_API` exposes init, memory copy, state copy, step, query, and status.
- `ARCHITECTURE_STATE_BLOB` contains diff-visible warp, PC, mask, register,
  predicate, memory-visible, launch, grid, CTA, and fault state.
- `GOLDEN_SIDECAR_STATE` contains synchronization aids such as scoreboard,
  outstanding memory, barrier phase, atomic pending, and debug query state.
- `STORE_COMMIT_EVENT` gives store errors an addressable commit channel.
- `GOLDEN_STATUS_API` separates running, done, faulted, aborted, and timeout state.

Rule: live diff mode must stay light and step with RTL events; offline analysis
mode handles profiling, checkpoints, and longer host-side attribution.

## perf_sampling_lessons

# Performance Sampling Lessons

XiangShan SimPoint/checkpoint/TopDown teaches that performance claims need
representative phases, replayable checkpoints, weights, counters, and
attribution. Toy kernels are smoke tests, not performance evidence.

GPGPU abstraction:

- `PHASE_FEATURE` records instruction mix, memory behavior, scheduling
  behavior, synchronization behavior, interval, and phase weight.
- `CHECKPOINT_PACKAGE` contains golden state, RTL snapshot, memory image,
  runtime descriptor, pending transactions, barrier/atomic state, schema
  versions, and replay commands.
- `WEIGHTED_PERF_REPORT` compares weighted phases and rejects regressions with
  explicit reasons.
- `TOPDOWN_GPGPU_ATTRIBUTION` partitions cycles into fetch/decode idle, warp
  scheduling stall, scoreboard stall, memory pipeline stall, synchronization
  stall, ALU/tensor busy, and structural conflict.

Rule: performance changes must pass correctness diff first, then representative
checkpoint replay, then weighted attribution.

## repo_map

# XiangShan Repo Map Lessons

XiangShan separates top-level configuration, simulation harness closure,
golden/reference infrastructure, differential testing, debug capture, runtime
constants, structured trace, scripts, and ready-to-run workloads.

GPGPU skill mapping:

- `gpgpu-architecture`: tool enablement switchboard and knob classification
- `gpgpu-contract`: executable reference machine and state blobs
- `gpgpu-toolchain-runtime`: launch descriptors, runtime knobs, debug knobs
- `gpgpu-rtl`: harness closure, probes, trace sinks, counter taps
- `gpgpu-validation`: diff, capture, trace DB, checkpoint replay, attribution
- `gpgpu-loop`: replay-driven rewrite routing and regression fingerprinting

Rule: generated workflows must produce reproducible scripts such as
`run_correctness.sh`, `run_diff.sh`, `run_replay.sh`,
`run_perf_sampling.sh`, `run_dse.sh`, and `collect_trace_db.sh`.

## runtime_dse_lessons

# Runtime DSE Lessons

XiangShan Constantin teaches that some design exploration should happen through
runtime-tunable constants, but only for behavior that has already been
elaborated into hardware.

GPGPU abstraction:

- `KNOB_CLASSIFICATION` separates structural compile-time, ABI-visible,
  runtime behavior, and debug trace knobs.
- `RUNTIME_DSE_KNOB` records name, default, value, bounds, class, metric, trace
  tables, and contamination risk.
- `RUNTIME_SWITCH_IR` records pre-elaborated variant selection with stable IO
  shape.
- `DSE_EXPERIMENT_MANIFEST` makes workload, correctness gate, performance gate,
  selected result, and rejection reason reproducible.

Rule: runtime knobs may change thresholds, policy selects, already-existing
feature enables, trace gates, and counter selection. They may not change module
existence, wire width, queue depth, bank count, warp size, ISA/ABI, or MMIO
layout.

## structured_trace_lessons

# Structured Trace Lessons

XiangShan ChiselDB teaches that high-cardinality debug and performance events
should be recorded as structured trace tables with queries, not only as VCD or
printf output.

GPGPU abstraction:

- `STRUCTURED_TRACE_TABLE` defines table name, schema version, common fields,
  producer, write gate, retention, and consumer skill.
- `TRACE_DB_MANIFEST` lists tables, schema versions, config hash, workload,
  producer build, and storage path.
- `SQL_DEBUG_QUERY` gives feature-specific root-cause queries.
- `SQL_PERF_QUERY` gives feature-specific attribution queries.

Required table families include warp issue/commit, scoreboard, memory
transaction, coalescer, cache access, MSHR, NoC packet, barrier, fence, atomic,
runtime launch, fault, and counter snapshot logs.

Rule: every memory, scheduling, sync, atomic, or performance feature must
provide at least one debug query and one performance attribution query.
