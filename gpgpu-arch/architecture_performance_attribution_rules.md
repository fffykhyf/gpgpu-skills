# Architecture-Level Performance Attribution Rules

Architecture changes for performance must follow this order:

1. launch and occupancy;
2. scheduler issue and non-issue;
3. scoreboard/dependency;
4. SIMT divergence/control;
5. memory request formation;
6. shared bank conflict;
7. L1 status and reservation fail;
8. MSHR;
9. ICNT request and return path;
10. L2/subpartition queue;
11. DRAM queue, row locality, and bank skew;
12. scoreboard release.

Do not tune DRAM before ruling out coalescing, L1/MSHR, ICNT, and L2 queues.

