# Memory Attribution Matrix

Memory attribution order:

1. warp transaction formation;
2. coalesced transaction count;
3. shared bank conflict;
4. L1 hit/miss/reservation status;
5. MSHR;
6. ICNT request path;
7. L2/subpartition queue;
8. DRAM queue/timing/row locality/bank skew;
9. return path;
10. scoreboard release.

