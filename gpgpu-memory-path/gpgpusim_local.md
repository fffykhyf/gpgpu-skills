# GPGPU-Sim Local Reference For GPGPU Memory Path

This note expands the GPGPU-Sim references that matter for the `gpgpu-memory-path` skill. It focuses on `ldst_unit`, `mem_fetch`, cache/MSHR behavior, L2/memory partitions, interconnect, DRAM timing, response routing, and memory statistics.

Terminology note: this file preserves GPGPU-Sim source names such as `warp`, `active_mask`, `CTA`, `shader`, and `memory partition`. In the skill contract, map them to `SIMT group`, active lane mask, CTA/workgroup, compute core/CU, and memory hierarchy owner names.

## What GPGPU-Sim Teaches For This Skill

GPGPU-Sim makes memory a staged path rather than a single load/store helper:

- `ldst_unit` receives dynamic warp instructions and splits shared, constant, texture, global, local, and parameter-local paths;
- cache access returns explicit statuses such as hit, miss, hit-reserved, and reservation fail;
- `mem_fetch` carries SIMT context and request metadata through the hierarchy;
- L1, ICNT, L2, memory sub-partition, DRAM scheduler, and response queues are separate owners;
- memory latency, cache, DRAM, and traffic stats are updated along the path.

For local work, copy the request lifecycle and backpressure vocabulary. Do not jump directly to full cache/DRAM complexity.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/gpgpusim.md` | Memory-path lessons and stage order. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/shader.cc` | `ldst_unit::{shared_cycle,constant_cycle,texture_cycle,memory_cycle,process_cache_access}`. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/shader.h` | LSU state, queues, response FIFO, interconnect injection. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/mem_fetch.*` | Request carrier fields, status, atomic handling. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/gpu-cache.*` | Cache, MSHR, miss queue, fill/data port pressure. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/l2cache.*` | Memory partition/sub-partition, L2/DRAM/ICNT queues, sector breakdown. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/dram.*` | DRAM bank timing, scheduler, return queue. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/icnt_wrapper.*` | Local interconnect or Intersim backend injection. |
| `ref_submodule/gpgpu-sim/src/gpgpu-sim/mem_latency_stat.*` | Memory latency attribution. |

## Memory Lifecycle To Borrow

| Stage | GPGPU-Sim owner | Local contract |
|---|---|---|
| issue to LSU | `ldst_unit` input pipeline | capture SIMT group, PC, op, active lane mask, destination |
| space split | `shared_cycle`, `constant_cycle`, `texture_cycle`, `memory_cycle` | classify shared/local/global/constant/texture or local equivalent |
| access generation | `warp_inst_t` memory accesses | preserve lane mask, per-lane address, size, and memory space |
| request carrier | `mem_fetch` | carry tag, SIMT context, size, op, stream/launch identity, status |
| L1/cache | `process_cache_access`, `gpu-cache` | model hit/miss/reservation fail/MSHR full separately |
| interconnect | `icnt_wrapper`, cluster injection | expose request queue full and routing metadata |
| L2/partition | `memory_sub_partition` | define L2 queues, sector split, DRAM queue admission |
| DRAM | `dram_t`, `dram_sched` | define scheduler, bank timing, return queue |
| response | response FIFO, store ack, writeback | demux by tag to SIMT group/lane/destination |
| stats | mem latency/cache/DRAM stats | record counters before claiming optimization |

## Backpressure And Status Vocabulary

Use explicit stall/status reasons:

- shared memory bank conflict;
- L1 bank conflict;
- cache miss;
- cache reservation fail;
- MSHR full;
- miss queue full;
- interconnect input/output full;
- L2 queue full;
- DRAM queue full;
- pending store/writeback dependency;
- memory fence or membar wait.

Do not collapse all of these into one `memory_stall` counter if the goal is to tune the memory path.

## Request Carrier Fields

A local `mem_fetch` equivalent should include:

- launch or stream ID if runtime has multiple queues;
- compute core/CU ID;
- simt_group_id;
- PC or instruction sequence ID;
- active lane mask;
- memory space;
- request type: load/store/atomic/fence;
- address, size, byte enable, and store data;
- destination register and writeback mask;
- request tag/transaction ID;
- ordering, cache policy, or bypass flag;
- status and timestamps for debug/statistics.

## Caveats

- GPGPU-Sim's memory hierarchy is rich enough to overwhelm an early RTL. Start with blocking LSU, then tags, response demux, coalescing, cache, MSHR, L2, DRAM.
- Timing statuses in C++ are not RTL handshakes. Translate them into valid-ready, queue capacity, and registered release paths.
- Texture/constant/PTX-specific paths may not exist in a local ISA; keep the staged memory-space split, not the exact CUDA feature set.

