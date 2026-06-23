# DRAM Queue / Scheduler Boundary Contract

Interconnect may report DRAM-facing queue boundaries but must not define DRAM
scheduling truth.

Evidence passed to memory skill:

- L2-to-DRAM queue occupancy;
- request arrival order;
- DRAM queue enter/exit cycle;
- row/bank/channel address fields when available.

