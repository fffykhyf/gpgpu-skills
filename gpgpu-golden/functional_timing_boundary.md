# Functional vs Timing Boundary

Golden semantics define correctness. Timing events explain performance.

Do not define a functional rule from:

- issue delay;
- scoreboard wait cycles;
- membar fixed stalls;
- cache latency;
- NoC/DRAM queue latency;
- power or visualization counters.

Fence, atomic, and barrier correctness must be defined by visibility,
serialization, return-value, and release conditions in `SYSTEM_CONTRACT_IR`.

