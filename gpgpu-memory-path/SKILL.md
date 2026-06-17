---
name: gpgpu-memory-path
description: Use when designing, editing, or debugging GPGPU memory behavior including LSU frontend/backend, lane masks, byte enables, outstanding requests, response demux, stores, loads, coalescing, banking, cache, MSHR, fences, stalls, or memory traces.
---

# GPGPU Memory Path

## Overview

Use this skill for LSU and memory-system work. Start with a blocking, traceable path, then add tags, response demux, coalescing, banking, cache, MSHR, fences, or VM only when correctness traces and counters justify the next step.

## Core Rule

Every memory request must be traceable by SIMT context:

- core ID, warp ID, PC or instruction ID
- active lane mask
- per-lane address or coalesced address
- byte enable and access width
- store data or load response data
- destination register or request tag
- response ordering rule
- stall, replay, fence, or exception reason when relevant

Do not make a memory optimization if the current trace and counters cannot show the problem it solves.

## Frontend And Backend Split

| Area | Owns |
|---|---|
| LSU frontend | AGU, address classification, byte enable, store-data alignment, fence lock, response formatting |
| Memory scheduler/backend | request queue, outstanding tag/index buffer, optional coalescing, batching, out-of-order response demux |
| Cache/bank layer | bank dispatch, hit/miss handling, MSHR, merge crossbar, flush, deadlock prevention |

Keep this split visible in simulator, RTL, trace, and tests.

## Stage Order

| Stage | Capability | Gate |
|---|---|---|
| M0 | blocking scalar load/store | single-lane load/store trace is correct |
| M1 | lane mask and byte enable | partial lane and access-width tests pass |
| M2 | vector lane memory | each lane address, data, and mask is traceable |
| M3 | outstanding loads | tag or index buffer routes out-of-order responses |
| M4 | coalescing | merge rate, replay, and partial response are explainable |
| M5 | bank/cache/MSHR | hit, miss, full queue, and deadlock tests exist |
| M6 | fence/flush/VM | ordering, translation, and unsupported behavior are explicit |

Skip stages only when the user asks for a focused study and the missing assumptions are documented.

## Non-Blocking Load Requirements

Any non-blocking load must specify:

- tag or index-buffer allocation and release.
- maximum outstanding requests.
- response demux path back to warp, lane mask, and destination.
- behavior on flush, kill, fence, exception, or queue-full.
- watchdog, assertion, or test that catches deadlock.

## Common Mistakes

- Adding cache before a working blocking LSU.
- Assuming in-order responses after introducing outstanding requests.
- Coalescing without preserving per-lane writeback, byte enables, and exception behavior.
- Losing the original warp/lane/destination metadata in the request tag.
- Treating final kernel output as the only memory correctness check.

For deeper Vortex background tied to this skill, read `vortex_local.md` in this directory. It summarizes the relevant Vortex design documents and code paths so routine LSU and memory-system work does not require re-reading the whole reference tree.
