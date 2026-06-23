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

