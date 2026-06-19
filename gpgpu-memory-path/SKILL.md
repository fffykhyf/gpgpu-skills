---
name: gpgpu-memory-path
description: Use when designing, editing, or debugging GPGPU memory behavior including LSU frontend/backend, lane masks, byte enables, outstanding requests, response demux, stores, loads, coalescing, banking, cache, MSHR, fences, stalls, or memory traces.
---

# GPGPU Memory Path

## Overview

Use this skill for LSU and memory-system work. Start with a blocking, traceable path, then add tags, response demux, coalescing, banking, cache, MSHR, fences, or VM only when correctness traces and counters justify the next step. Use Rocket Chip's HellaCache, DCache, and TileLink as references for request/response schemas, source ID lifetime, replay/nack/kill semantics, ordering, protocol helpers, monitors, and constrained fuzzing. Use XiangShan as the reference for a fully documented LSU/LSQ/replay/cache/MMU/L2 lifecycle, especially replay-cause priority, violation handling, vector metadata, and counter attribution.

## Core Rule

Every memory request must be traceable by SIMT context:

- compute core/CU ID, simt_group_id, PC or instruction ID
- active lane mask
- per-lane address or coalesced address
- byte enable and access width
- store data or load response data
- destination register or request tag
- source ID or outstanding index lifetime
- response ordering rule
- stall, nack, replay, kill, fence, flush, or exception reason when relevant
- address space, translation state, and cacheability/MMIO classification when relevant
- cache/memory status when modeled: hit, miss, reservation fail, MSHR full, queue full, ICNT full, or DRAM wait

Do not make a memory optimization if the current trace and counters cannot show the problem it solves.

For non-trivial memory paths, define a protocol schema in addition to the trace: op, size, address, byte mask, active lane mask, data, tag/source ID, ordering scope, cacheability, fault fields, and response metadata. Treat this as an executable contract with assertions or monitors.

## Terminology Contract

Use canonical terms for memory traces and tags. Keep source aliases only when naming RTL signals.

| Canonical term | Source aliases | Memory-path meaning |
|---|---|---|
| SIMT group | warp, wavefront, wave | execution group that issues memory operations |
| simt_group_id | warp ID, `wfid`, wave ID, wavefront tag | request/response identity for a resident SIMT group |
| active lane mask | active mask, lane mask, thread mask, `EXEC` mask | lanes that participate in a load/store |
| CTA/workgroup | CTA, block, workgroup | local-memory and barrier scope |
| compute core/CU | core, CU, compute unit | memory-client owner |

## Frontend And Backend Split

| Area | Owns |
|---|---|
| LSU frontend | AGU, address classification, byte enable, store-data alignment, fence lock, response formatting |
| Memory scheduler/backend | request queue, outstanding tag/index buffer, optional coalescing, batching, out-of-order response demux |
| Cache/bank layer | bank dispatch, hit/miss handling, MSHR, merge crossbar, flush, deadlock prevention |
| Protocol/check layer | source/tag validity, alignment, mask legality, ordering, replay/nack/fault, monitor/fuzzer hooks |

Keep this split visible in simulator, RTL, trace, and tests.

## GPGPU-Sim Memory Lifecycle

Use GPGPU-Sim as the reference for a staged request path:

| Stage | GPGPU-Sim anchor | Local rule |
|---|---|---|
| issue to LSU | `ldst_unit` input pipeline | capture SIMT group, PC, op, active lane mask, destination |
| space split | `shared_cycle`, `constant_cycle`, `texture_cycle`, `memory_cycle` | classify memory space before cache behavior |
| request carrier | `mem_fetch` | preserve SIMT context, tag, address, size, op, status, and response route |
| L1/cache | `process_cache_access`, `gpu-cache` | distinguish hit, miss, hit-reserved, reservation fail, MSHR/miss-queue pressure |
| interconnect | `icnt_wrapper`, cluster injection | expose routing and backpressure instead of assuming free network |
| L2/partition | `memory_sub_partition` | define L2 queues, sector split, and DRAM admission |
| DRAM | `dram_t`, `dram_sched` | define bank timing, scheduling, return queue |
| response | response FIFO, store ack, writeback | demux by tag to SIMT group, lane mask, and destination |
| stats | memory latency/cache/DRAM stats | measure before claiming optimization |

Do not collapse these owners into a single black-box memory model once the design grows beyond a blocking LSU.

## Rocket Chip Memory Contract

Use Rocket Chip as the reference for making memory protocols explicit:

| Contract | Rocket Chip anchor | Local rule |
|---|---|---|
| request schema | `HellaCacheReq`, TileLink A/C channels | Carry op, size, address, mask, data, tag/source ID, privilege/address-space, and no-response/no-allocate semantics explicitly. |
| response schema | `HellaCacheResp`, TileLink D channel | Carry data, replay, denied/fault, metadata, destination, and source/sink identity explicitly. |
| exceptional flow | DCache kill/nack/replay/flush/probe/release/grant | Specify behavior for kill, flush, nack, replay, fence, fault, uncached/MMIO, and outstanding requests. |
| derived helpers | `tilelink/Edges.scala` | Centralize beat, mask, first/last/done, source, and address calculations. |
| executable checks | `tilelink/Monitor.scala`, `tilelink/Fuzzer.scala` | Add monitors and constrained random traffic before claiming protocol robustness. |
| resource params | `DCacheParams`, MSHR/MMIO/source ID ranges | Configure and check queue depths, MSHRs, MMIO slots, and source/tag ranges in one place. |

Translate TileLink ideas into the local GPGPU protocol; do not assume a CPU cache coherence protocol is the GPU memory model.

## XiangShan LSU Replay Pattern

Use XiangShan as the reference for memory paths where replay, violation, and wakeup are first-class design objects:

| Memory contract | XiangShan anchor | Local memory-path rule |
|---|---|---|
| backend-memory boundary | `MemBlock.scala` | Define issue, LSQ enqueue, commit, redirect, violation, exception, wakeup, writeback, and perf ports. |
| load/store queue owner | `LSQWrapper.scala` | Keep load queue, store queue, bypass, forward, uncache, rollback, hint, and debug ownership explicit. |
| replay cause enum | `LoadQueueReplay.scala` | Enumerate replay reasons and preserve priority ordering with deadlock reasoning. |
| vector metadata | `VecReplayInfo`, vector LSU files | Carry per-element, mask, merge-buffer, offset, and active metadata when vector or lane replay exists. |
| cache/TLB path | `DCacheWrapper.scala`, `cache/mmu/` | Derive source IDs, MSHR entries, TLB/PTW misses, uncache/MMIO, ECC, and prefetch fields from config. |
| shared L2/backpressure | PDF CoupledL2 chapter, `L2Top.scala` | Document MSHR, retry/credit, MMIO bridge, error, and downstream protocol behavior. |

Local GPGPU memory work should name replay causes such as coalescer retry, shared-memory bank conflict, TLB miss, cache miss, MSHR full, NoC backpressure, atomic serialization, uncache/MMIO, fault, and store/load ordering. If two causes can be true at once, write the priority and prove it cannot deadlock.

A first blocking LSU should name its FSM states and trace:

| Area | Required evidence |
|---|---|
| issue capture | simt_group_id, PC, opcode, memory format, destination, SGPR/VGPR class |
| address generation | scalar base, vector offset, immediate, thread id, LDS base, global/LDS bit |
| lane control | active lane mask, skipped lanes, per-lane address vector |
| request | read/write enable, address, write data, write mask, tag |
| response | ack, tag, read data, destination register, writeback mask |
| completion | done simt_group_id, retire PC, memory wait release, trace event |

Only after this path passes load/store, masked-lane, global/LDS, and SGPR/VGPR writeback tests should coalescing, cache, MSHR, or VM be treated as implementation work rather than speculation.

## Stage Order

| Stage | Capability | Gate |
|---|---|---|
| M0 | blocking scalar load/store | single-lane load/store trace is correct |
| M1 | lane mask and byte enable | partial lane and access-width tests pass |
| M2 | vector lane memory | each lane address, data, and mask is traceable |
| M3 | outstanding loads | tag or index buffer routes out-of-order responses |
| M4 | coalescing | merge rate, replay, and partial response are explainable |
| M5 | bank/cache/MSHR/L2/ICNT | hit, miss, full queue, routing, and deadlock tests exist |
| M6 | fence/flush/VM | ordering, translation, and unsupported behavior are explicit |

Skip stages only when the user asks for a focused study and the missing assumptions are documented.

## Non-Blocking Load Requirements

Any non-blocking load must specify:

- tag or index-buffer allocation and release.
- maximum outstanding requests.
- source ID or tag visibility at every queue, coalescer, cache, interconnect, and response point.
- response demux path back to SIMT group, lane mask, and destination.
- behavior on flush, kill, fence, exception, or queue-full.
- behavior on cache reservation failure, interconnect backpressure, and response FIFO full when those layers exist.
- watchdog, assertion, or test that catches deadlock.
- monitor or trace assertion for tag reuse, mask legality, alignment, replay, and response completion.

## Common Mistakes

- Adding cache before a working blocking LSU.
- Assuming in-order responses after introducing outstanding requests.
- Coalescing without preserving per-lane writeback, byte enables, and exception behavior.
- Losing the original SIMT-group/lane/destination metadata in the request tag.
- Reporting one generic memory stall after adding cache, interconnect, L2, or DRAM queues.
- Treating final kernel output as the only memory correctness check.
- Hand-coding beat/mask/source calculations in several places instead of centralizing derived protocol helpers.
- Adding replay, nack, or out-of-order response support without a source/tag lifetime checker.
- Adding replay causes without a XiangShan-style priority table, owner counter, and deadlock check.

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains the LSU scheduler, memory unit, coalescer/cache/MSHR boundaries, and full-stack memory contracts.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the MIAOW LSU opcode decoder, address calculator, op-manager FSM, simple memory model, trace signals, and limitations.

For deeper GPGPU-Sim background tied to this skill, read `gpgpusim_local.md` in this directory. It explains `ldst_unit`, `mem_fetch`, cache/MSHR status, L2/memory partitions, interconnect, DRAM timing, response routing, and memory statistics.

For Rocket Chip background tied to this skill, read `../../ref/skillref/rocket.md` and then inspect `../../ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala`, `rocket/DCache.scala`, `tilelink/Bundles.scala`, `tilelink/Edges.scala`, `tilelink/Monitor.scala`, `tilelink/Fuzzer.scala`, and `diplomacy/Parameters.scala` when needed.

For XiangShan background tied to this skill, read `xiangshan_local.md` in this directory. It explains the PDF LSU/DCache/MMU/CoupledL2 chapters, `MemBlock`, `LSQWrapper`, `LoadQueueReplay`, DCache parameters, TLB/PTW structure, vector replay metadata, and how to adapt those details to GPGPU memory paths.
