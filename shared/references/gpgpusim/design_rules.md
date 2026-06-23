# GPGPU-Sim Derived Design Rules

These rules are imported methodology, not copied implementation.

1. Classify before copying: every external parameter is `hardware-private`,
   `simulator-private`, `HW/SW ABI`, `test-only`, or `debug-only`.
2. Separate functional semantics from timing behavior. A stall cannot define
   correctness.
3. Issue must explain non-issue with explicit reasons.
4. Keep SIMT control state separate from scoreboard dependency state.
5. Memory request formation is a first-class boundary.
6. Memory stalls are layered: formation, shared/L1, cache/MSHR, ICNT, L2,
   DRAM, return path, scoreboard release.
7. Cache miss and reservation failure are different root-cause families.
8. NoC contracts preserve packet class, source, destination, byte size, flits,
   and buffer result.
9. DRAM tuning requires address mapping, row locality, queue, and bank-skew
   evidence.
10. Synchronization is not just a stall; atomics, fences, and barriers need
    correctness contracts and timing stall counters.
11. Visualization variables require producer audit.
12. Power is derivative of activity counters.
13. Tested configs are profiles, not defaults.
14. Regression must gate counters, not only functional output.
15. NVIDIA-specific CUDA/PTX/SASS behavior requires an optional compatibility
    profile.

Raw basis: `raw/gpgpu-sim-design-rules-for-gpgpu-skills.md`.

