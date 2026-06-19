# XiangShan Local Reference For GPGPU Memory Path

This note expands the XiangShan references that matter for the `gpgpu-memory-path` skill. It focuses on the LSU/LSQ boundary, replay causes and priority, DCache parameters, MMU/TLB/PTW, CoupledL2, vector replay metadata, and memory performance events.

Terminology note: XiangShan memory code is CPU load/store-queue code. Preserve names such as LoadQueue, StoreQueue, ROB, uncache, TLB, DCache, and CoupledL2 when discussing XiangShan. In local GPGPU contracts, translate the lesson to SIMT group, active lane mask, lane replay, coalescer, shared/global memory, memory partition, source/tag, and kernel/runtime fault semantics.

## What XiangShan Teaches For This Skill

XiangShan is the strongest local reference for memory-path discipline. Its memory design makes request lifecycle, replay reasons, fault paths, cache/TLB state, L2 backpressure, and perf events explicit.

Borrow these habits:

- define backend-memory interface fields;
- split load queue, store queue, replay, uncache/MMIO, and hints;
- enumerate replay causes and priority;
- preserve vector/lane metadata through replay;
- derive cache/TLB/source ID fields from config;
- place counters near memory event owners.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/xiangshan.md` | Memory-path lessons and seven-skill mapping. |
| `ref/xiangshan.pdf` | LSU, DCache, MMU, CoupledL2 chapters. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/MemBlock.scala` | Backend-memory bundle, issue, LSQ enqueue, commit, wakeup, writeback, violation, perf. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/lsqueue/LSQWrapper.scala` | Load/store queue wrapper, forward, bypass, replay, rollback, uncache, CMO, hints, debug. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/mem/lsqueue/LoadQueueReplay.scala` | Replay cause enum, priority, vector replay info, counters. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/dcache/DCacheWrapper.scala` | DCache params, source IDs, ECC, MSHR/probe/release/MMIO entries, prefetch source. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/mmu/` | ITLB/DTLB/L2TLB/PTW/PMP/PMA style address-translation structure. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/cache/wpu/` | Wait/prediction structures related to memory behavior. |
| `ref_submodule/xiangshan/src/main/scala/xiangshan/L2Top.scala` | L2/top memory hierarchy integration. |

## Backend-Memory Boundary

`MemBlock.scala` defines the memory block as a real boundary between backend and memory. It includes:

- issue inputs for load/store/vector memory units;
- LSQ enqueue;
- commit and redirect signals;
- SFENCE, CSR, TLB CSR;
- load/store wakeup and writeback;
- memory violation and mdpTrain;
- exception address and MMIO busy;
- load queue/store queue accept and cancel;
- debug and perf outputs.

For local GPGPU memory path, define the equivalent boundary with:

- issue packet fields: simt_group_id, PC, active lane mask, op, address metadata, destination;
- request acceptance and backpressure;
- replay/fault/wakeup/writeback response fields;
- per-lane or coalesced metadata;
- trace and counter exports.

## LSQWrapper Ownership

`LSQWrapper.scala` instantiates LoadQueue and StoreQueue and wires:

- branch redirect and rollback;
- load/store enqueue and canAccept;
- store address/data;
- bypass, forward, replay;
- store buffer and uncache;
- MMIO and CMO paths;
- load wakeup and release;
- L2/TLB hints;
- debugTopDown and diffStore hooks.

The local rule is to avoid a monolithic LSU. Even if the first design is blocking, name the owners for AGU, queue, replay, coalescer, cache request, response demux, and trace.

## Replay Cause Priority

`LoadQueueReplay.scala` enumerates replay causes such as:

- uncache;
- store multi-forward invalid;
- memory ambiguity;
- TLB miss;
- store-to-load forwarding fail;
- DCache replay;
- DCache miss;
- WPU prediction fail;
- bank conflict or unaligned split fail;
- RAR/RAW queue reject;
- nuke;
- miss queue full.

The source and PDF warn that priority changes may cause deadlock. This is directly relevant to GPGPU memory. Local replay reasons should include coalescer retry, shared-memory bank conflict, TLB miss, cache miss, MSHR full, NoC backpressure, atomic serialization, uncache/MMIO, fault, and memory-ordering conflicts. If more than one cause can apply, write a priority table and a deadlock argument.

## Vector Replay Metadata

`VecReplayInfo` carries vector replay metadata such as vector flag, last element, element index, aligned type, merge-buffer index, register offset, active flag, first element, and mask.

For a GPGPU lane memory path, this translates to:

- lane mask and per-lane address;
- coalesced segment metadata;
- partial response mask;
- merge buffer or response-buffer index;
- destination register and lane offset;
- fault/replay mask;
- active lane state at replay time.

## DCache, MMU, And L2

`DCacheWrapper.scala` shows that cache params are not just sets and ways. They include ECC, replacement, miss/probe/release/MMIO entries, prefetch entries, cache control address, source types, request ID width, masks, tags, alias bits, uncache IDs, and `require` checks.

The PDF MMU chapter covers ITLB/DTLB, L2TLB, page table walker, PMP/PMA, hints, miss queues, and virtualization translation. Local GPGPU work may not need all of this, but if virtual addressing exists, TLB miss, fault, retry, and page-walk ownership must be explicit.

The CoupledL2 chapter covers MSHRs, directory/inclusive behavior, TileLink/CHI, retry/credit, MMIO bridge, ECC/DataCheck/Poison, and error handling. Local GPGPU L2/interconnect work should define MSHR ownership, source ID lifetime, retry/backpressure, MMIO bypass, error/fault response, and counters.

## Caveats

- XiangShan LSQ is CPU load/store ordering, not GPU memory coalescing.
- CPU ROB-based violation handling is not a GPU warp/CTA ordering model.
- CPU DCache coherence policy is not automatically a GPU memory consistency model.
- Borrow replay priority, request lifecycle, and counter ownership; do not copy CPU memory semantics blindly.
