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

