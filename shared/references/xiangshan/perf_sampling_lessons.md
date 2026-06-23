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
