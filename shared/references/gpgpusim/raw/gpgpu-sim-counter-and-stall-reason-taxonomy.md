# GPGPU-Sim Counter And Stall Reason Taxonomy

Source repo: `ref_submodule/gpgpu-sim`

Primary files:

- `src/gpgpu-sim/stats.h`
- `src/gpgpu-sim/shader.cc`
- `src/gpgpu-sim/gpu-sim.cc`
- `src/gpgpu-sim/gpu-cache.{h,cc}`
- `src/gpgpu-sim/l2cache.cc`
- `src/gpgpu-sim/dram.cc`
- `src/gpgpu-sim/mem_latency_stat.*`
- `src/gpgpu-sim/visualizer.cc`
- `aerialvision/variableclasses.py`
- `aerialvision/lexyacc.py`
- `src/gpgpu-sim/power_interface.cc`
- `src/gpgpu-sim/power_stat.h`

## Status Classes

- `live`: reader agents found a source-side producer in the current commit.
- `defined-but-not-proven-live`: enum/printer/parser entry exists, but no active producer was found in the pass.
- `parser-only`: AerialVision parser declares the name, but current producer audit did not prove emission.

## Shader / Scheduler Counters

| Counter / field | Status | Meaning | Source | Attribution use |
|---|---|---|---|---|
| `shader_cycle_distro[0]` | live | idle/control bucket | `src/gpgpu-sim/shader.cc:scheduler_unit::cycle` | control/fetch/no-ready work |
| `shader_cycle_distro[1]` | live | scoreboard wait bucket | `src/gpgpu-sim/shader.cc:scheduler_unit::cycle`, `scoreboard.cc` | dependency bottleneck |
| `shader_cycle_distro[2+]` | live | issue/active-lane distribution | `src/gpgpu-sim/shader.cc:shader_core_ctx::issue_warp` | utilization / lane efficiency |
| `single_issue_nums` | live | single-issue count | `src/gpgpu-sim/shader.cc` | scheduler utilization |
| `dual_issue_nums` | live | dual-issue count | `src/gpgpu-sim/shader.cc` | dual-issue effectiveness |
| `WarpIssueSlotBreakdown` | live | issue slot breakdown | `src/gpgpu-sim/shader.cc:shader_core_stats::visualizer_print` | scheduler imbalance |
| `WarpIssueDynamicIdBreakdown` | live | dynamic warp issue distribution | `src/gpgpu-sim/shader.cc` | fairness / warp residency |
| `WarpDivergenceBreakdown` | live | divergence distribution | `src/gpgpu-sim/shader.cc`, `aerialvision/lexyacc.py` | branch/SIMT cost |
| `shaderinsncount` | live | per-shader instruction count | `src/gpgpu-sim/shader.cc` | shader load balance |
| `shaderwarpinsncount` | live | per-shader warp instruction count | `src/gpgpu-sim/shader.cc` | SIMT issue work |
| `shaderwarpdiv` | live | per-shader divergence | `src/gpgpu-sim/shader.cc` | control-flow bottleneck |

## Memory Stage Stall Reasons

Enum source: `src/gpgpu-sim/stats.h:mem_stage_stall_type`

| Stall reason | Status | Meaning | Main producer / evidence | Attribution rule |
|---|---|---|---|---|
| `NO_RC_FAIL` | live | no resource failure | `ldst_unit::*` | baseline/no stall |
| `BK_CONF` | live | bank conflict | `ldst_unit::shared_cycle`, `process_memory_access_queue_l1cache` | shared/L1 bank layout or access pattern |
| `MSHR_RC_FAIL` | defined-but-not-proven-live | MSHR resource fail | enum/printer exists | require producer audit before first-class use |
| `ICNT_RC_FAIL` | live | ICNT injection/resource fail | `ldst_unit::memory_cycle` | NoC/partition ingress backpressure |
| `COAL_STALL` | live | access queue not drained after coalescing | `ldst_unit::process_memory_access_queue*` | coalescing fragmentation or request amplification |
| `TLB_STALL` | defined-but-not-proven-live | TLB stall | enum exists | legacy/inactive until proven |
| `DATA_PORT_STALL` | live | cache data-port pressure | cache/LSU access path | L1 data port bottleneck |
| `WB_ICNT_RC_FAIL` | defined-but-not-proven-live | writeback ICNT fail | enum/printer exists | require producer audit |
| `WB_CACHE_RSRV_FAIL` | defined-but-not-proven-live | writeback cache reservation fail | enum/printer exists | require producer audit |

Access-type dimension: `src/gpgpu-sim/stats.h:mem_stage_access_type`

- `C_MEM`
- `T_MEM`
- `S_MEM`
- `G_MEM_LD`
- `L_MEM_LD`
- `G_MEM_ST`
- `L_MEM_ST`

Design implication: memory stalls should always be reported as `(access_type, stall_reason)`.

## Cache Counters

Source:

- `src/gpgpu-sim/gpu-cache.h`
- `src/gpgpu-sim/gpu-cache.cc`

Cache request status:

| Status | Meaning | Attribution |
|---|---|---|
| `HIT` | tag/data hit | cache effective |
| `HIT_RESERVED` | line hit but reserved | structural conflict |
| `MISS` | cache miss | locality/capacity/conflict |
| `RESERVATION_FAIL` | cache could not accept request | queue/MSHR/line allocation pressure |
| `SECTOR_MISS` | sector miss in sector cache | sector utilization issue |
| `MSHR_HIT` | miss merged with existing MSHR | MLP exists but completion still pending |

Reservation fail reasons:

- `LINE_ALLOC_FAIL`
- `MISS_QUEUE_FULL`
- `MSHR_ENRTY_FAIL`
- `MSHR_MERGE_ENRTY_FAIL`
- `MSHR_RW_PENDING`

Report rule: never merge `MISS` and `RESERVATION_FAIL`; they imply different fixes.

## ICNT / Traffic Counters

| Counter / field | Status | Meaning | Source | Attribution |
|---|---|---|---|---|
| `gpu_stall_icnt2sh` | live | return path cannot inject to shader/cluster | `src/gpgpu-sim/gpu-sim.cc:gpgpu_sim::cycle` | memory-to-shader congestion |
| `icnt_total_pkts_mem_to_simt` | live | packets from memory to SIMT clusters | `src/gpgpu-sim/shader.cc` | return traffic volume |
| `icnt_total_pkts_simt_to_mem` | live | packets from SIMT to memory | `src/gpgpu-sim/shader.cc` | request traffic volume |
| `traffic_breakdown_coretomem[...]` | live | request-class traffic breakdown | `src/gpgpu-sim/traffic_breakdown.*` | traffic mix |
| `traffic_breakdown_memtocore[...]` | live | response-class traffic breakdown | `src/gpgpu-sim/traffic_breakdown.*` | response mix |

## DRAM / Partition Counters

| Counter / field | Status | Meaning | Source | Attribution |
|---|---|---|---|---|
| `gpu_stall_dramfull` | live | memory partition / DRAM ingress full | `src/gpgpu-sim/gpu-sim.cc` | partition/L2/DRAM queue bottleneck |
| `gpgpu_n_dram_*` | live | DRAM command/activity counts | `l2cache.cc`, `dram.cc` | DRAM activity |
| `n_cmd`, `n_activity`, `n_req`, `n_rd`, `n_wr`, `n_wr_WB` | live | DRAM commands/requests/read/write/writeback | `src/gpgpu-sim/dram.cc` | bandwidth use |
| `dram_util_bins`, `dram_eff_bins` | live | utilization/efficiency distribution | `dram.cc` | raw bandwidth bottleneck |
| `maxmflatency` | live | max memory fetch latency | `mem_latency_stat.*` | tail latency |
| `max_icnt2mem_latency` | live | max ICNT-to-memory latency | `mem_latency_stat.*` | interconnect/partition delay |
| `maxmrqlatency` | live | max DRAM request queue latency | `mem_latency_stat.*` | DRAM queueing |
| row locality tables | live | row hit/locality behavior | `dram_sched.*`, `mem_latency_stat.*` | address mapping / FR-FCFS |
| bank/chip skew | live | request distribution skew | `mem_latency_stat.*`, `addrdec.*` | partitioning/address mapping |
| `position_of_mrq_chosen` | live when memlat stat enabled | chosen DRAM queue position | `mem_latency_stat.cc` | scheduler behavior |

## Visualization Variables

Producer-backed examples:

- `globalcyclecount`
- `globalinsncount`
- `globaltotinsncount`
- `WarpDivergenceBreakdown`
- `WarpIssueSlotBreakdown`
- `WarpIssueDynamicIdBreakdown`
- `shaderinsncount`
- `shaderwarpinsncount`
- `shaderwarpdiv`
- `Ltwowritemiss`
- `Ltwowritehit`
- `Ltworeadmiss`
- `Ltworeadhit`
- `averagemflatency`
- `dramncmd`
- `dramnop`
- `dramnact`
- `dramnpre`
- `dramnreq`
- `dramavemrqs`
- `dramutil`
- `drameff`
- `dramglobal_acc_*`
- `dramlocal_acc_*`
- `dramconst_acc_r`
- `dramtexture_acc_r`

Parser-only or producer-not-proven examples:

- `gpu_stall_by_MSHRwb`
- `dram_reads_per_cycle`
- `dram_writes_per_cycle`
- `cacheMissRate_*`
- `globalSentWrites`
- `globalProcessedWrites`

Rule: `gpgpu-simppa` should require a producer audit before adding any AerialVision variable as a stable metric.

## Power Counters

Power is derived from existing performance counters through `src/gpgpu-sim/power_interface.cc`:

- instruction totals and committed instructions;
- int/fp/dp/sfu/tensor/texture access counts;
- register file reads/writes;
- L1I/L1D/L2 hit/miss counts;
- shared/constant/texture accesses;
- active SMs;
- average pipeline duty cycle;
- active lanes and active threads;
- DRAM read/write/precharge counts;
- ICNT flits in both directions.

Rule: AccelWattch results are derivative estimates, not independent performance evidence.

## Skill Patch Requirement

`gpgpu-simppa` should add:

- source category: producer-backed / defined-only / parser-only;
- access-type plus stall-reason matrix;
- cache status plus reservation-fail matrix;
- partition/ICNT/DRAM queue attribution;
- power counter provenance.
