# Performance Attribution Order

Use this order before changing design knobs:

1. launch and occupancy;
2. scheduler issue and non-issue;
3. scoreboard and dependency;
4. SIMT divergence and control;
5. memory request formation;
6. shared memory bank conflict;
7. L1 cache status and reservation fail;
8. MSHR;
9. ICNT request path;
10. L2/subpartition queue;
11. DRAM queue, row locality, and bank skew;
12. return path;
13. scoreboard release;
14. power or energy derivative.

Every root cause must include symptom counter, exclusion counter, queue or stage
owner, possible fix target, and confidence. A conclusion without a counter path
is `INSUFFICIENT_TRACE_EVIDENCE`.

Raw basis: `raw/gpgpu-sim-performance-attribution-methodology.md`.

