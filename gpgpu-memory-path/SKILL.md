---
name: gpgpu-memory-path
description: Use when designing, editing, or debugging GPGPU memory behavior including LSU, global memory, local memory, lane masks, byte enables, memory requests, stores, loads, coalescing, banking, cache, MSHR, fences, memory stalls, or memory traces.
---

# GPGPU Memory Path

## Overview

Use this skill for LSU and memory-system work. Start with a blocking, traceable memory path and add coalescing, banking, cache, and MSHR only when counters and traces show why they are needed.

## Core Rule

Every memory request must be traceable by SIMT context:

- core and warp ID
- PC or instruction ID
- active lane mask
- address per participating lane or coalesced address
- byte enable
- store data or load response data
- request tag or destination register
- stall, replay, or response reason when relevant

Do not make a memory optimization if the current trace and counters cannot show the problem it solves.

## Stage Order

1. Blocking LSU with aligned word loads/stores.
2. Lane mask and byte enable support.
3. Outstanding request tracking with simple tags.
4. Load response demux and writeback trace.
5. Memory stall counters and bandwidth counters.
6. Coalescing for same-line or compatible lane requests.
7. Banking and arbitration.
8. Cache, non-blocking cache, MSHR, TLB, VM, and fences.

Skip stages only when the user explicitly asks for a focused study and the missing assumptions are documented.

## Design Checklist

For each memory feature, answer:

- Is the issue bandwidth, latency, serialization, bank conflict, replay, ordering, or coherence?
- Is the behavior architectural or only a timing optimization?
- What is the response ordering rule?
- What happens when some lanes are inactive?
- What happens on partial stores or unaligned accesses?
- What counter will show improvement or regression?
- What trace will expose an incorrect request or response?

## Common Mistakes

- Adding cache before a working blocking LSU.
- Coalescing requests without preserving per-lane writeback and exception behavior.
- Losing byte-enable information in the trace.
- Assuming in-order responses while introducing outstanding requests.
- Using final kernel output as the only memory correctness check.
