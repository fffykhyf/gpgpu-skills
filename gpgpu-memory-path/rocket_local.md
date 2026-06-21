# Rocket Chip Local Reference For GPGPU Memory Path

This note expands the Rocket Chip references that matter for the `gpgpu-memory-path` skill. It focuses on HellaCache/DCache request-response contracts, nack/replay/kill/ordered behavior, TileLink fields, edge helpers, protocol monitors, fuzzers, source-ID lifetime, and memory perf events.

Terminology note: Rocket Chip memory code is CPU cache and TileLink logic. Preserve names such as HellaCache, DCache, TileLink, MSHR, MMIO, TLB, nack, replay, and source ID when discussing Rocket. In local GPGPU memory work, translate the pattern to SIMT group, active lane mask, coalescer transaction, memory space, scope, source/tag, replay/fault, and lane writeback.

## What Rocket Chip Teaches For This Skill

Rocket's memory path is useful because the request and response contract is explicit and checkable:

- request/response bundles carry command, size, address, mask, data, tag/source, fault, replay, and metadata;
- DCache handles TLB/PMA, meta/data arrays, ECC, MSHR/refill, uncached/MMIO, probes, flush, nack, replay, and ordering;
- TileLink bundles and edge helpers centralize masks, beats, first/last/done, source, address, and hasData;
- monitors track multibeat stability and in-flight source IDs;
- fuzzers generate legal traffic.

## Reference Orientation

| Path | What to look for |
|---|---|
| `ref/skillref/rocket.md` | Memory-path lessons and seven-skill mapping. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala` | `DCacheParams`, `HellaCacheReq`, `HellaCacheResp`, `HellaCacheIO`, perf events, source ranges. |
| `ref_submodule/rocket-chip/src/main/scala/rocket/DCache.scala` | TLB/PMA, nack/replay, uncached in-flight, store pending, ordered, probe/release/grant. |
| `ref_submodule/rocket-chip/src/main/scala/tilelink/Bundles.scala` | A/B/C/D/E channel fields: opcode, param, size, source, sink, address, mask, data, corrupt, denied. |
| `ref_submodule/rocket-chip/src/main/scala/tilelink/Edges.scala` | `mask`, `hasData`, `first`, `last`, `done`, `firstlast`, request/response helpers. |
| `ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala` | Source/sink in-flight tracking and multibeat field stability checks. |
| `ref_submodule/rocket-chip/src/main/scala/tilelink/Fuzzer.scala` | Legal memory traffic, source allocation/free, in-flight pressure. |

## HellaCache Contract

`HellaCacheReq` carries address, command, size, signedness, privilege/address-space state, physical/virtual hints, no-response/no-allocate/no-exception flags, data, and mask. `HellaCacheResp` includes replay, has_data, data, store data, and exception metadata. `HellaCacheIO` exposes req/resp, kill, s2_nack, raw-hazard hint, replay_next, exceptions, ordered, store_pending, and perf events.

Local GPGPU request/response schemas should add:

- compute core/CU ID;
- simt_group_id;
- active lane mask;
- per-lane or coalesced address mapping;
- memory space and scope;
- atomic/fence semantics;
- replay/fault mask;
- destination lane/register metadata.

## DCache And Exceptional Paths

`DCache.scala` shows that memory is not just hit/miss. It handles TLB miss, raw/waw hazards, nacks, uncached in-flight responses, probe/release/grant, ordered/store_pending, replay_next, ECC, flush, and cache-control behavior.

Local memory-path rules:

- do not add nonblocking requests without source/tag lifetime checks;
- do not collapse nack, replay, TLB miss, MSHR full, queue full, uncached/MMIO, and ordering stalls into one reason;
- define kill/flush/fence/fault priority;
- place counters near LSU/coalescer/cache owners.

## TileLink Lessons

TileLink's most useful transfer ideas are:

- complete channel field schema;
- source/sink ID lifecycle;
- edge helpers for mask/beat/first/last/done;
- executable protocol monitors;
- constrained legal fuzzers.

A local GPGPU protocol need not be TileLink, but it must have equivalent clarity for lane masks, coalescing, address space, ordering, and response routing.

## Caveats

- Rocket DCache coherence is CPU-oriented; do not treat it as the GPU memory model.
- TileLink lacks GPU-specific SIMT/lane/coalescer fields.
- HellaCache is a request/response discipline reference, not a complete GPGPU memory hierarchy.
