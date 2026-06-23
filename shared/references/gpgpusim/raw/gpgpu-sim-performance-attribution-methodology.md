# GPGPU-Sim Performance Attribution Methodology

Source repo: `ref_submodule/gpgpu-sim`

Goal: translate GPGPU-Sim's counters and stall reasons into a reusable attribution method for simple-gpgpu skills.

## Attribution Order

Use this order before changing design knobs:

1. Confirm workload/launch shape.
2. Check occupancy/resource fit.
3. Check scheduler and scoreboard stalls.
4. Check memory-formation stalls at LSU.
5. Check L1/cache status and reservation fail reasons.
6. Check ICNT request/response pressure.
7. Check L2/subpartition/ROP queues.
8. Check DRAM timing, row locality, and bank/chip skew.
9. Check power only after performance counters are stable.

## Rules

| Symptom | Counters / evidence | Likely bottleneck | First files to inspect | Design response |
|---|---|---|---|---|
| low issue rate, high `shader_cycle_distro[1]` | `shader_cycle_distro`, scoreboard collision, long-op loads | register dependency / long memory dependency | `shader.cc`, `scoreboard.cc` | change scheduling, reduce dependency chain, expose scoreboard wait |
| low issue rate, high occupancy limit pressure | CTA fit, registers/shared memory/thread limit | resource residency | `shader.cc:occupy_shader_resource_1block`, config | tune resource allocation, occupancy contract |
| high `BK_CONF` | `gpu_stall_shd_mem_breakdown[*][BK_CONF]`, shared/L1 bank config | shared or L1 bank conflict | `shader.cc`, `abstract_hardware_model.cc` | adjust banking/layout or access pattern |
| high `COAL_STALL` | access queue remains after coalescing | fragmented memory transactions | `abstract_hardware_model.cc`, `shader.cc` | inspect coalescer and transaction granularity |
| high `DATA_PORT_STALL` | L1 data-port pressure | cache port bottleneck | `shader.cc`, `gpu-cache.cc` | adjust cache port/pipeline model |
| high `ICNT_RC_FAIL` | LSU memory cycle ICNT fail | request injection pressure | `shader.cc`, `icnt_wrapper.cc` | inspect ICNT buffer/push contract |
| high `gpu_stall_icnt2sh` | return packets, cluster response FIFO, LSU response FIFO | memory-to-shader return congestion | `gpu-sim.cc`, `shader.cc` | increase return-path capacity or reduce read amplification |
| high `gpu_stall_dramfull` | partition queue full, L2 reservation fails | L2/subpartition/DRAM ingress pressure | `gpu-sim.cc`, `l2cache.cc`, `gpu-cache.cc` | inspect L2 queues before DRAM timing |
| high cache `RESERVATION_FAIL` | fail reasons `MISS_QUEUE_FULL`, `MSHR_*`, `LINE_ALLOC_FAIL` | structural cache pressure | `gpu-cache.cc` | adjust MSHR/miss queue, write policy, sectoring |
| high `SECTOR_MISS` | sector cache stats | sector waste / poor locality | `gpu-cache.cc`, coalescer | change transaction granularity or locality |
| high `max_icnt2mem_latency` | mem latency stats | ICNT/partition delay | `mem_latency_stat.*`, `l2cache.cc` | address ICNT/partition queues |
| high `maxmrqlatency`, low `drameff` | DRAM queue latency and efficiency | raw DRAM scheduler/timing | `dram.cc`, `dram_sched.cc` | adjust address mapping, FR-FCFS, bank-group policy |
| high bank/chip skew | memory-latency skew tables | address partitioning imbalance | `addrdec.cc`, config mapping | change address mapping/indexing |
| power spike with no matching perf counter | AccelWattch component power and source mode | power-model artifact or counter mapping | `power_interface.cc`, `accelwattch` | audit counter provenance first |

## Memory-Performance Taxonomy

The memory path must be reported in layers:

1. warp request formation;
2. coalesced transaction count;
3. shared/L1 bank conflict;
4. L1 hit/miss/reservation status;
5. MSHR state;
6. ICNT injection;
7. L2 subpartition queues;
8. DRAM queue and bank scheduler;
9. return path to shader;
10. scoreboard release / warp unblock.

If a report jumps from "load is slow" directly to "DRAM is slow", it is incomplete.

## Required Report Fields

Every future reader report should include:

- workload/kernel name if known;
- launch shape and occupancy;
- dominant scheduler stall;
- dominant memory stall tuple `(access_type, stall_reason)`;
- cache status distribution;
- ICNT request/return pressure;
- L2/partition queue pressure;
- DRAM utilization/efficiency/row locality;
- evidence path for each claim;
- simulator-only caveats.

## Design Rule

Rule name: performance conclusion requires a counter path

Problem solved: avoids unsupported bottleneck guesses.

Required state contract:

- stage where request is blocked;
- resource that is full or waiting;
- event that releases it.

Required config contract:

- every proposed knob must be classified before tuning.

Required counter/stall reason:

- at least one counter for symptom and one for downstream exclusion.

Applicable skill:

- `gpgpu-simppa`
- `gpgpu-memory`
- `gpgpu-interconnect`
- `gpgpu-arch`

Implementation anchor:

- `src/gpgpu-sim/stats.h`
- `src/gpgpu-sim/shader.cc`
- `src/gpgpu-sim/gpu-cache.cc`
- `src/gpgpu-sim/l2cache.cc`
- `src/gpgpu-sim/dram.cc`
- `src/gpgpu-sim/mem_latency_stat.cc`
