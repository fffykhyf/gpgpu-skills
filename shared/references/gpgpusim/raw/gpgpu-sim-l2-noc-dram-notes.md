# GPGPU-Sim L2 / NoC / DRAM Notes

Source repo: `ref_submodule/gpgpu-sim`

Primary files:

- `src/gpgpu-sim/mem_fetch.{h,cc}`
- `src/gpgpu-sim/mem_fetch_status.tup`
- `src/gpgpu-sim/l2cache.{h,cc}`
- `src/gpgpu-sim/icnt_wrapper.{h,cc}`
- `src/gpgpu-sim/local_interconnect.*`
- `src/intersim2/*`
- `src/gpgpu-sim/dram.{h,cc}`
- `src/gpgpu-sim/dram_sched.{h,cc}`
- `src/gpgpu-sim/addrdec.*`

## Mem Fetch Lifecycle

`mem_fetch` adds simulator transport state around a `mem_access_t`:

- request id;
- warp/core/cluster provenance;
- raw and partitioned address;
- control size and data size;
- timestamps;
- current `mem_fetch_status`;
- original request pointers for sector-split traffic.

Important statuses from `mem_fetch_status.tup`:

- `MEM_FETCH_INITIALIZED`
- `IN_L1I_MISS_QUEUE`
- `IN_L1D_MISS_QUEUE`
- `IN_L1T_MISS_QUEUE`
- `IN_L1C_MISS_QUEUE`
- `IN_ICNT_TO_MEM`
- `IN_PARTITION_ICNT_TO_L2_QUEUE`
- `IN_PARTITION_L2_TO_DRAM_QUEUE`
- `IN_PARTITION_DRAM_LATENCY_QUEUE`
- `IN_PARTITION_L2_MISS_QUEUE`
- `IN_PARTITION_MC_*`
- `IN_PARTITION_DRAM`
- `IN_PARTITION_DRAM_TO_L2_QUEUE`
- `IN_PARTITION_L2_FILL_QUEUE`
- `IN_PARTITION_L2_TO_ICNT_QUEUE`
- `IN_ICNT_TO_SHADER`
- `MEM_FETCH_DELETED`

Transferable:

- a normalized memory request lifecycle trace.

Simulator-only:

- exact status names;
- exact queue partitioning and C++ FIFO classes.

## L2 And Memory Partition

Primary owner:

- `memory_sub_partition`
- `memory_partition_unit`

Observed queues:

- `m_icnt_L2_queue`
- `m_L2_dram_queue`
- `m_dram_L2_queue`
- `m_L2_icnt_queue`
- ROP delay queue before L2 handling

Observed behavior:

- sector caches can split one request into multiple 32B sector requests before L2.
- L2 hits return through `m_L2_icnt_queue`.
- L2 misses go into `m_L2_dram_queue`.
- `memory_partition_unit` arbitrates subpartitions, applies credit logic, and stages requests toward DRAM.

Performance implication:

- high `gpu_stall_dramfull` can mean L2/subpartition/ROP queue backpressure before raw DRAM timing is the bottleneck.

## Interconnect / NoC

Interface:

- `icnt_has_buffer`
- `icnt_push`
- `icnt_pop`
- `icnt_transfer`
- `icnt_busy`
- `icnt_drain`
- `icnt_display_stats`

Backend selection:

- `-network_mode 1`: Intersim/BookSim path.
- `-network_mode 2`: local xbar path.

Important SM86 finding:

- `configs/tested-cfgs/SM86_RTX3070/gpgpusim.config` uses `-network_mode 2`.
- Therefore `config_ampere_islip.icnt` is not active for this tested profile unless the config is changed.

LocalInterconnect caveat:

- reader agents found it assumes one-flit packets with fixed 40B flits in the local path.
- packet-size semantics are more explicit in the Intersim path.

RTL contract candidate:

- preserve `has_buffer/push/pop` with packet class, source, destination, size/flits, and backpressure.

Simulator-only:

- BookSim allocator/VC knobs as hardware truth;
- local-xbar one-flit simplification unless intentionally adopted.

## DRAM Model

Primary files:

- `dram.cc`
- `dram.h`
- `dram_sched.cc`
- `dram_sched.h`

State:

- banks and bank groups;
- current row per bank;
- counters for timing blockers such as RCD/RAS/RP/RC/CCD/RRD/CCDL;
- read/write queues;
- FR-FCFS scheduler bins per bank/row;
- return queue.

Config:

- `-gpgpu_dram_scheduler`
- `-gpgpu_frfcfs_dram_sched_queue_size`
- `-gpgpu_dram_return_queue_size`
- `-gpgpu_dram_buswidth`
- `-gpgpu_dram_burst_length`
- `-dram_data_command_freq_ratio`
- `-gpgpu_mem_addr_mapping`
- `-gpgpu_dram_timing_opt`
- `-dram_bnk_indexing_policy`
- `-dram_bnkgrp_indexing_policy`
- `-dram_dual_bus_interface`
- `-dram_latency`

Observed DRAM behavior:

- FR-FCFS favors row hits.
- `dram_t` issues `ACT`, `PRE`, `RD`, and `WR`.
- timing constraints include `tRRD`, `tCCD`, `tRCD`, `tRAS`, `tRP`, `tRC`, `tCL`, `tWL`, `tCCDL`, `tRTPL`.
- visualizer/counters report utilization, efficiency, request counts, row locality, and bank/chip skew.

Simulator-only:

- fixed `dram_latency` stage between partition and DRAM;
- credit heuristic in `memory_partition_unit`;
- exact queue sizes from SM86 config.

## Performance Attribution Rules

- High `gpu_stall_icnt2sh` plus return packet growth: return path or response FIFO congestion.
- High `gpu_stall_dramfull`: partition/L2/DRAM ingress backpressure; inspect L2 queues before DRAM timing.
- High `max_icnt2mem_latency` or `maxmrqlatency`: request spends too long between ICNT and memory queue.
- Low `drameff` or poor row locality: address mapping, FR-FCFS, or bank-group policy issue.
- High bank/chip skew: memory partition indexing or address mapping issue.

## Design Rule

Rule name: memory hierarchy reports must name the queue boundary

Problem solved: distinguishes L2/subpartition, ICNT, and DRAM bottlenecks.

Required state contract:

- memory request lifecycle status;
- subpartition queue occupancy;
- ICNT buffer status;
- DRAM bank/row/timing state;
- response path availability.

Required counter/stall reason:

- `gpu_stall_dramfull`
- `gpu_stall_icnt2sh`
- L2 hit/miss/fail stats
- DRAM utilization/efficiency
- row locality
- bank/chip skew
- max/average memory latency

Applicable skill:

- `gpgpu-memory`
- `gpgpu-interconnect`
- `gpgpu-simppa`

Implementation anchor:

- `src/gpgpu-sim/l2cache.cc`
- `src/gpgpu-sim/icnt_wrapper.cc`
- `src/gpgpu-sim/dram.cc`
- `src/gpgpu-sim/dram_sched.cc`
