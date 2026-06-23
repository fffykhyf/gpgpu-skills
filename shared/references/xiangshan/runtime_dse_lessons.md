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

