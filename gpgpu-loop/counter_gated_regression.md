# Counter-Gated Regression

Functional pass does not imply regression pass.

Trigger rewrite when:

- coalesced transaction count unexpectedly increases;
- scoreboard wait rises without explanation;
- barrier/membar/atomic wait lacks a sync contract;
- cache reservation fail spikes;
- ICNT `has_buffer` fail spikes;
- L2 queue full is misattributed to DRAM;
- a counter lacks producer proof.

## XiangShan Weighted Perf Gate

Performance rewrite decisions must consume `WEIGHTED_PERF_REPORT` and
`TOPDOWN_GPGPU_ATTRIBUTION` when representative checkpoints exist. Reject a
performance patch when correctness diff fails, checkpoint replay is missing, a
high-weight phase regresses without owner explanation, or debug trace knobs
contaminate the measured ranking.
