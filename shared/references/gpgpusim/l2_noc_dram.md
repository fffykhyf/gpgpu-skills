# L2, NoC, and DRAM Queue Boundary Rules

Memory hierarchy attribution must name the queue boundary where a request waits:

- SM/LSU to ICNT request injection;
- ICNT to L2 subpartition;
- L2 miss queue;
- L2 to DRAM queue;
- DRAM scheduling/timing queue;
- DRAM to L2 return queue;
- L2 to ICNT return queue;
- ICNT to shader response FIFO;
- scoreboard release.

NoC packet contracts must preserve packet class, source, destination, byte size,
flit count, VC class if used, buffer result, push cycle, and pop cycle.

DRAM bottlenecks require evidence for queue occupancy or latency plus at least
one of row locality, bank/chip skew, scheduler command activity, utilization, or
efficiency. Do not conclude "DRAM is slow" from high memory latency alone.

Raw basis: `raw/gpgpu-sim-l2-noc-dram-notes.md`.

