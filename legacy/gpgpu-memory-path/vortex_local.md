# Vortex Local Reference For GPGPU Memory Path

This note expands the Vortex references that matter for the `gpgpu-memory-path`
skill. It focuses on LSU frontend/backend separation, lane masks, byte enables,
tags, coalescing, caches, fences, VM, and simulator/RTL trace alignment.

Terminology note: this file preserves Vortex source names such as `warp`, `warp ID`, `tmask`, and `CTA`. In the skill contract, map them to `SIMT group`, `simt_group_id`, `active lane mask`, and `CTA/workgroup`; use Vortex names only when quoting source behavior.

## What Vortex Teaches For This Skill

Vortex does not treat memory as a black-box load/store function. The path is
split into layers with clear ownership:

- LSU frontend: AGU, address classification, byte enable, store data alignment,
  fence lock, and response formatting.
- Memory scheduler/backend: request queue, load index buffer, optional
  coalescer, batching, response demux, and watchdogs.
- Cache/bank/memory layer: bank selection, merge/response crossbar, MSHR,
  flush, local memory, MMU, and deadlock prevention.
- Simulator mirror: LSU unit, local-memory switch, coalescer, cache adapters,
  memory request/response payloads, and counters.

For this project, copy the staged discipline. Start with a traceable blocking
path, then add outstanding loads, coalescing, cache, and VM only when the trace
can prove correctness.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/vortex.md` | Local extraction of staged memory-path lessons. |
| `ref_submodule/vortex/docs/designs/lsu_pipeline_design.md` | Detailed LSU frontend/backend design and response demux rules. |
| `ref_submodule/vortex/docs/cache_subsystem.md` | Cache bank dispatch, merge crossbar, MSHR, flush, and deadlock notes. |
| `ref_submodule/vortex/docs/designs/simx_simulator_architecture.md` | SimX memory graph: LSU, coalescer, local memory, cache, DRAM, `MemReq`, `MemRsp`. |
| `ref_submodule/vortex/docs/hardware_library.md` | Elastic buffers, arbiters, allocators, counters, and reusable flow-control blocks. |
| `ref_submodule/vortex/VX_config.toml` | LSU lanes, LSU queue sizes, cache sizes/ways/MSHR, memory block size, local memory settings. |
| `ref_submodule/vortex/VX_types.toml` | Memory map, local memory map, cache counters, memory counters, TLB/PTW counters. |

## RTL LSU Frontend

`ref_submodule/vortex/hw/rtl/core/VX_lsu_slice.sv` is the best concrete
frontend reference.

Important behaviors:

- The AGU computes per-lane `full_addr = rs1 + offset`.
- Address attributes are computed per lane and carried as sideband metadata:
  IO address, local memory address, flush/fence, and optional AMO metadata.
- AMO requests carry operation, signed/unsigned flavor, and a packed hart id.
  When atomic extension is disabled, the sideband is tied off to avoid unknowns
  propagating into downstream checks.
- Store/load width becomes byte-enable masks. 8-bit, 16-bit, 32-bit, and 64-bit
  accesses shift the byte-enable according to low address bits.
- Store data is shifted/aligned to match the byte-enable lane.
- Misaligned memory accesses are explicitly asserted against in simulation.
- Fence handling uses `fence_lock`; a fence can block new memory requests until
  the corresponding response unlocks it.
- Store-without-response and skipped fence packets go through a no-response
  result buffer so commit/writeback semantics stay ordered.
- Request tags pack the instruction header, op type, per-lane alignment, packet
  index, and fence bit. This is what lets the response formatter reconstruct
  destination and packet metadata.
- Load response formatting sign-extends or zero-extends byte/half/word data,
  handles RV64/F32 NaN-boxing, restores the active response mask, and forwards
  SOP/EOP packet markers.

Local transfer rule: a memory request must carry enough original SIMT metadata
to reconstruct writeback without guessing from response order.

## Multi-Packet And PID Tracking

`VX_lsu_slice.sv` also shows how packetized loads are tracked when a warp
request can be split across multiple memory packets.

If `PID_BITS != 0`, the frontend keeps:

- a packet allocator;
- per-packet counters;
- SOP and EOP flags;
- a collision case when request and response touch the same packet entry;
- assertions for allocator full and malformed SOP sequences.

This is a useful reference if the local design supports vector-lane memory,
coalesced line requests, or any out-of-order response path. The key idea is not
the exact counter implementation; it is that SOP/EOP cannot be inferred from
the final response alone once requests are split.

## Memory Scheduler Backend

`ref_submodule/vortex/hw/rtl/libs/VX_mem_scheduler.sv` is the generic backend
reference. It is parameterized by core request lanes, memory channels, word/line
size, tag width, queue sizes, optional response partial mode, and output
buffering.

Important pieces:

- A request queue holds core requests after checking whether load index-buffer
  space is available.
- Loads allocate an index-buffer entry; stores do not need a return entry.
- The outgoing memory tag combines UUID bits, index-buffer address, and batch
  index. The response tag later recovers the original core tag.
- Optional `VX_mem_coalescer` merges multiple word requests into line requests
  when the line size is larger than the word size.
- Large merged requests are emitted in batches across available memory
  channels. The batch index becomes part of the memory tag.
- Responses either return partial packets (`RSP_PARTIAL`) or store pieces until
  all lanes for a request are complete.
- A remaining-mask table tracks which lanes of a multi-lane request still need
  a response.
- Simulation watchdog state catches requests that never receive a response.
- Debug traces include core request, memory request, memory response, core
  response, tags, and UUIDs.

For local memory work, do not introduce out-of-order responses without an
index-buffer/tag/release story. Do not introduce coalescing without preserving
per-lane byte enables and response reconstruction.

## Core Memory Unit And Cache Layer

`ref_submodule/vortex/hw/rtl/core/VX_mem_unit.sv`,
`ref_submodule/vortex/hw/rtl/cache/`, and
`ref_submodule/vortex/hw/rtl/mem/` are the downstream references.

Use the docs more than the full RTL on first pass:

- `docs/cache_subsystem.md` explains bank dispatch, response merge, MSHR, flush,
  and deadlock concerns.
- `docs/hardware_library.md` explains reusable elastic buffers, arbiters,
  allocators, and counters that appear in the memory path.
- `VX_config.toml` shows the knobs that control memory complexity:
  `VX_CFG_MEM_BLOCK_SIZE`, `VX_CFG_NUM_LSU_LANES`, `VX_CFG_LSU_LINE_SIZE`,
  `VX_CFG_LSUQ_IN_SIZE`, `VX_CFG_LSUQ_OUT_SIZE`, cache sizes, ways, MSHR sizes,
  bank counts, local memory log size, and TLB size.

If this project is still at a blocking LSU stage, use these as later-stage
references. Cache and MSHR are not prerequisites for a correct memory contract.

## Simulator Memory Mirror

`ref_submodule/vortex/sim/simx/core.cpp` constructs the SimX memory graph:

- per-LSU-block `MemCoalescer` objects;
- `LocalMem`;
- `LocalMemSwitch`;
- dcache and local-memory adapters;
- optional per-core dcache and icache `Mmu`;
- core cache ports for instruction and data paths.

The constructor explicitly binds local-memory and dcache paths. When local
memory is enabled, accesses can route through `LocalMemSwitch`; with VM enabled,
dcache requests pass through an MMU before reaching the cache hierarchy.

`ref_submodule/vortex/sim/simx/types.h` defines `MemReq` and `MemRsp`:

- `MemReq`: operation, address, data block, byte enable, tag, hart id, UUID,
  flags, plus helpers for write/read and address type.
- `MemRsp`: tag, hart id, UUID, and optional data block.

These types are a good local trace template. A golden memory trace should expose
op, address, byte enable, tag, response, and SIMT context. It should not be only
`addr -> data`.

## SimX LSU Unit

`ref_submodule/vortex/sim/simx/lsu_unit.cpp` is the simulator-side counterpart
to the RTL LSU path.

Relevant behaviors:

- `compute_addrs()` builds a per-thread address/size/data list from decoded
  operands and active mask. It uses `rs1 + stride * rs2 + offset` for regular
  LSU uops and handles AMO as a separate typed operation.
- `ingest_inputs()` moves at most one trace into the request queue per cycle,
  preserving a real queue stage instead of creating zero-latency passthrough.
- A fence at the queue head waits until older per-block requests have drained.
- `process_request_step()` sends at most one memory-side batch per cycle,
  allocates pending entries for loads/AMOs, stores lane metadata, preserves
  original thread id, sets UUID and core id, and emits a `LsuReq`.
- `process_response_step()` consumes one response packet, finds the pending
  entry by tag, formats load data, handles byte selection and NaN-boxing, and
  forwards the trace only on terminal response.
- `pending_loads_` feeds load-latency counters.

This is the model to emulate when building a local golden simulator for memory:
traceable pending state, not just direct loads/stores.

## Counters And Debug Signals

`ref_submodule/vortex/VX_types.toml` gives useful counter categories:

- core-level LSU counts: loads, load latency, stores;
- cache-level reads/writes, read misses, write misses, evictions, bank stalls,
  MSHR stalls;
- memory-level reads, writes, memory latency, memory bank stalls;
- local-memory reads/writes and bank stalls;
- coalescer misses;
- TLB lookups, hits, misses, evictions, PTW walks, PTW latency.

Use these categories when adding local counters. A memory optimization is hard
to justify if the trace cannot show correctness and the counters cannot show
what bottleneck changed.

## Local Stage Plan

Use Vortex as a staged reference:

| Stage | Capability | Required proof |
|---|---|---|
| M0 | blocking scalar load/store | address, width, byte-enable, data trace is correct |
| M1 | active lane mask and partial width | divergent lanes and subword tests pass |
| M2 | vector-lane memory | per-lane address/data/mask is traceable |
| M3 | outstanding loads | tag/index-buffer routes out-of-order responses |
| M4 | coalescing | merge/miss/partial-response behavior is observable |
| M5 | cache/bank/MSHR | hit/miss/full/bank/deadlock tests exist |
| M6 | fence/flush/VM | ordering and translation contracts are explicit |

## What Not To Copy

- Do not add cache/MSHR/VM before the LSU contract is traceable.
- Do not assume in-order response after introducing outstanding loads.
- Do not coalesce away lane metadata.
- Do not copy Vortex queue depths or cache sizes without local PPA evidence.
- Do not treat final kernel output as the only memory correctness signal.
