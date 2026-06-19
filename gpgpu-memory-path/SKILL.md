---
name: gpgpu-memory-path
description: Use when designing, editing, or debugging GPGPU memory behavior including LSU frontend/backend, lane masks, byte enables, outstanding requests, response demux, stores, loads, coalescing, banking, cache, MSHR, fences, stalls, or memory traces.
---

# GPGPU Memory Path

## Overview

Use this skill for LSU and memory-system work. Start with a blocking, traceable path, then add tags, response demux, coalescing, banking, cache, MSHR, fences, or VM only when correctness traces and counters justify the next step.

## Core Rule

Every memory request must be traceable by SIMT context:

- compute core/CU ID, simt_group_id, PC or instruction ID
- active lane mask
- per-lane address or coalesced address
- byte enable and access width
- store data or load response data
- destination register or request tag
- response ordering rule
- stall, replay, fence, or exception reason when relevant
- cache/memory status when modeled: hit, miss, reservation fail, MSHR full, queue full, ICNT full, or DRAM wait

Do not make a memory optimization if the current trace and counters cannot show the problem it solves.

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
- response demux path back to SIMT group, lane mask, and destination.
- behavior on flush, kill, fence, exception, or queue-full.
- behavior on cache reservation failure, interconnect backpressure, and response FIFO full when those layers exist.
- watchdog, assertion, or test that catches deadlock.

## Common Mistakes

- Adding cache before a working blocking LSU.
- Assuming in-order responses after introducing outstanding requests.
- Coalescing without preserving per-lane writeback, byte enables, and exception behavior.
- Losing the original SIMT-group/lane/destination metadata in the request tag.
- Reporting one generic memory stall after adding cache, interconnect, L2, or DRAM queues.
- Treating final kernel output as the only memory correctness check.

## Local References

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It explains the LSU scheduler, memory unit, coalescer/cache/MSHR boundaries, and full-stack memory contracts.

For deeper MIAOW background tied to this skill, read `miao_local.md` in this directory. It explains the MIAOW LSU opcode decoder, address calculator, op-manager FSM, simple memory model, trace signals, and limitations.

For deeper GPGPU-Sim background tied to this skill, read `gpgpusim_local.md` in this directory. It explains `ldst_unit`, `mem_fetch`, cache/MSHR status, L2/memory partitions, interconnect, DRAM timing, response routing, and memory statistics.
