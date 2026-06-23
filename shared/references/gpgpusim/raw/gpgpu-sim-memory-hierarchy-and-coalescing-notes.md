# GPGPU-Sim Memory Hierarchy And Coalescing Notes

Source repo: `ref_submodule/gpgpu-sim`

Primary files:

- `src/abstract_hardware_model.{h,cc}`
- `src/gpgpu-sim/shader.{h,cc}`
- `src/gpgpu-sim/gpu-cache.{h,cc}`
- `src/gpgpu-sim/mem_fetch.{h,cc}`
- `src/gpgpu-sim/stats.h`
- `configs/tested-cfgs/SM86_RTX3070/gpgpusim.config`

## Request Formation

The most transferable request schema is `mem_access_t`:

- memory access type;
- address;
- size;
- write/read;
- warp active mask;
- byte mask;
- sector mask.

`warp_inst_t::generate_mem_accesses()` is the important boundary:

- shared-memory operations compute bank conflicts and set latency/dispatch cycles;
- global/local accesses call architecture-dependent coalescing;
- atomics use a distinct coalescing path that splits overlapping byte ranges when required;
- generated transactions enter `warp_inst_t::m_accessq`.

Design rule: simple-gpgpu should define a normalized `warp_memory_transaction` contract before defining cache/NoC/DRAM behavior.

## Coalescing

Relevant source:

- `warp_inst_t::memory_coalescing_arch`
- `warp_inst_t::memory_coalescing_arch_atomic`
- `warp_inst_t::memory_coalescing_arch_reduce_and_send`

Observed behavior:

- `-gpgpu_coalesce_arch 86` selects an NVIDIA-generation-specific coalescing model.
- for `gpgpu_coalesce_arch >= 40`, requests are sector-aware and can reduce toward 32B sectors.
- coalescing is per warp/subwarp and uses active/byte/sector masks.

Transferable:

- input: per-lane addresses, access size, active mask, access type.
- output: ordered list of masked transactions.
- counter hooks: number of generated accesses, coalescing stalls, sector amplification.

Do not copy:

- exact NVIDIA-generation segment rules as final simple-gpgpu ABI;
- exact SM86 sector size unless the memory subsystem intentionally chooses it.

## Shared Memory And Bank Conflicts

Primary source:

- `src/gpgpu-sim/shader.cc:ldst_unit::shared_cycle`

Observed behavior:

- shared memory does not become a lower-level `mem_fetch`.
- bank conflicts are modeled as dispatch delay.
- `BK_CONF` is recorded when shared memory cannot complete because of bank conflict delay.
- config knobs include `-gpgpu_shmem_num_banks`, `-gpgpu_shmem_limited_broadcast`, `-gpgpu_shmem_warp_parts`, `-gpgpu_smem_latency`.

RTL contract candidate:

- shared-memory bank mapping;
- conflict count or conflict class per warp request;
- stall reason: `shared_bank_conflict`.

Simulator-only:

- fixed `smem_latency` value;
- C++ dispatch-delay implementation.

## L1 And Cache Status Taxonomy

Primary source:

- `src/gpgpu-sim/gpu-cache.h`
- `src/gpgpu-sim/gpu-cache.cc`

Cache request status:

- `HIT`
- `HIT_RESERVED`
- `MISS`
- `RESERVATION_FAIL`
- `SECTOR_MISS`
- `MSHR_HIT`

Reservation fail reasons:

- `LINE_ALLOC_FAIL`
- `MISS_QUEUE_FULL`
- `MSHR_ENRTY_FAIL`
- `MSHR_MERGE_ENRTY_FAIL`
- `MSHR_RW_PENDING`

Design implication:

- cache performance attribution should separate tag outcome from resource outcome. A miss is not the same as a reservation failure.

## LSU Events

Primary source:

- `src/gpgpu-sim/shader.cc:ldst_unit::*`

Important events:

- `func_exec_inst()` calls memory access generation before timing issue.
- `ldst_unit::issue()` increments pending writes by access-queue count.
- cache hit/fill decrements pending writes and can release scoreboard registers.
- stores receive acknowledgments.
- `memory_cycle()` either bypasses L1D, probes L1D, or pushes into ICNT.
- `process_memory_access_queue_l1cache()` records `BK_CONF`, `COAL_STALL`, and data-port/cache statuses.

## Config Parameters

Hardware-private:

- `-gpgpu_cache:dl1`
- `-gpgpu_l1_banks`
- `-gpgpu_l1_cache_write_ratio`
- `-gpgpu_gmem_skip_L1D`
- `-gpgpu_cache:il1`
- `-gpgpu_tex_cache:l1`
- `-gpgpu_const_cache:l1`
- shared-memory size/banks/broadcast/warp-parts
- `-gpgpu_coalesce_arch`

Simulator-private / guarded:

- `-gpgpu_l1_latency`
- `-gpgpu_smem_latency`
- `-gpgpu_perfect_inst_const_cache`
- `-gpgpu_flush_l1_cache`

HW/SW ABI relevant:

- per-block shared memory and register resource limits;
- global memory L1D bypass behavior if exposed to compiler/cache operators.

## Performance Attribution Rules

- `BK_CONF`: shared-memory or L1 bank conflict; inspect bank mapping and warp access pattern.
- `COAL_STALL`: access queue still contains transactions; inspect transaction amplification and coalescing granularity.
- `DATA_PORT_STALL`: L1 data-port pressure; inspect cache port/latency model and request mix.
- `ICNT_RC_FAIL`: lower-level injection failure; inspect ICNT/partition queue availability before blaming DRAM.
- High `MSHR_HIT` with high latency can mean memory-level parallelism exists but return path or DRAM still dominates.

## Design Rule

Rule name: classify memory stalls at formation, cache, and transport separately

Problem solved: avoids attributing all memory latency to DRAM.

Required state contract:

- per-warp generated transaction count;
- per-transaction masks;
- L1/cache status;
- MSHR state;
- ICNT injection result;
- pending write count.

Required counter/stall reason:

- bank conflict;
- coalescing stall;
- cache hit/miss/sector miss;
- reservation fail reason;
- ICNT resource fail;
- pending-write release latency.

Applicable skill:

- `gpgpu-memory`
- `gpgpu-rtl`
- `gpgpu-simppa`

Implementation anchor:

- `src/abstract_hardware_model.cc:warp_inst_t::generate_mem_accesses`
- `src/gpgpu-sim/shader.cc:ldst_unit::memory_cycle`
- `src/gpgpu-sim/gpu-cache.h`
