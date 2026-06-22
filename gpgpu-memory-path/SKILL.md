---
name: gpgpu-memory-path
description: Use when designing, editing, or debugging GPGPU memory behavior including LSU frontend/backend, lane masks, byte enables, outstanding requests, response demux, stores, loads, coalescing, banking, cache, MSHR, fences, stalls, or memory traces.
---

# GPGPU Memory State Machine Skill

## 1. Objective

Implement memory as a state machine over address spaces, lane masks, cache/coalescer state, outstanding requests, ordering, and responses, rather than as a list of LSU/cache/NoC blocks.

## 2. Input Contract

Input is a memory behavior intent with issue packet schema, config digest, address spaces, mask/byte rules, ordering/fence requirements, cache/coalescer scope, and oracle alignment target.

## 3. Memory State Model

| State | Fields |
|---|---|
| address space state | global, shared/LDS, local, constant, MMIO/uncached, cacheability, translation/fault status |
| coherence/visibility state | host/device visibility, fence scope, flush state, atomic serialization, cache ownership when modeled |
| cache line state | tag, valid/dirty, sector bits, MSHR ownership, fill/evict state |
| outstanding request table | tag/source ID, simt_group_id, PC, op, lane mask, byte mask, destination, response route |
| coalescer state | per-lane address groups, segment merge, split requests, partial response mapping |
| pipeline state | issue, coalesce, tag lookup, miss/refill, response, retire/replay |
| hazard state | bank conflict, miss, queue full, ordering wait, replay/nack, fault, deadlock watchdog |

## 4. Mandatory Five Questions

For every memory change answer:

1. What state exists? Name address, cache, outstanding, coalescer, ordering, or pipeline state.
2. Who produces it? LSU, coalescer, cache, interconnect, DRAM, response demux, or runtime fence.
3. Who consumes it? SIMT scheduler, register writeback, cache, runtime, oracle, trace, or PPA.
4. How does it change? Define issue, merge, miss, fill, response, replay, fence, flush, and fault transitions.
5. How do we verify it? Name memory trace, monitor, oracle alignment, directed test, or counter check.

## 5. Access Contract

Every access must carry:

- kernel ID, compute core/CU ID, simt_group_id, PC or instruction ID.
- op: load, store, atomic, fence, flush, prefetch, or unsupported.
- address space and cacheability.
- active lane mask, per-lane address, byte enable, width, alignment.
- store data or destination register mapping.
- tag/source ID and response route.
- ordering scope and fence/atomic semantics.
- fault/replay/kill eligibility.

## 6. Warp Coalescing Rule

Coalescing is a transformation from lane accesses to one or more memory transactions:

```text
lane requests + active mask -> segment groups -> memory transactions -> partial responses -> per-lane writeback/fault
```

Rules:

- Semantic result must match uncoalesced per-lane execution.
- Coalesced transactions must preserve byte enables, lane ownership, destination mapping, and fault metadata.
- Partial responses must retire only the lanes they cover.
- Replays must restore lane ownership without duplicating stores or dropping load destinations.

## 7. Transformation Rules: Memory Pipeline

The canonical memory FSM is:

```text
issue -> coalesce -> tag -> miss -> fill -> retire
```

| Stage | Input state | Transformation | Output state |
|---|---|---|---|
| issue | SIMT issue packet | validate op, masks, address space, alignment | memory request candidate |
| coalesce | per-lane requests | group/split lanes into transactions | transaction list and lane map |
| tag | transaction | allocate outstanding entry/source ID | in-flight request |
| miss | cache/bank/interconnect state | hit, miss, queue, replay, bank conflict, fault | response wait or replay |
| fill | downstream response | update cache/MSHR/outstanding table | response payload |
| retire | response payload | write back loads, commit stores/atomics, clear waits | memory trace and scheduler release |

For a blocking LSU, keep the same stages but allow only one in-flight request.

## 8. Hazard Model

| Hazard | Required rule |
|---|---|
| bank conflict | conflict detection, stall/replay priority, counter owner |
| cache miss | MSHR allocation, miss queue full behavior, fill ownership |
| response ordering | in-order or out-of-order rule, tag lifetime, demux assertion |
| memory dependency | load/store/atomic/fence ordering scope and scoreboard interaction |
| queue pressure | full conditions, backpressure path, no-drop assertion |
| replay/nack | replay cause enum, priority, state restoration, deadlock proof |
| fault | address/access fault state, per-lane reporting, completion semantics |
| flush/kill | outstanding request behavior, response ignore or drain rule |

If two hazards can be true together, define priority and the trace field that records it.

## 9. State Evolution

| Event | State change |
|---|---|
| LSU accepts issue packet | capture PC, mask, op, address metadata, destination |
| address generation | produce per-lane addresses and byte masks |
| coalescer accepts | allocate lane-to-transaction map |
| tag allocation | create outstanding request entry and block dependent SIMT group |
| cache hit | return response or store commit through retire stage |
| cache miss/MSHR allocate | track fill state and downstream route |
| replay/nack/full | preserve request and release/retry according to priority |
| response arrives | demux by tag/source to SIMT group, lane mask, destination |
| retire | update register file or store visibility, clear memory wait |
| fence/flush | update ordering/coherence state and runtime visibility |
| fault | record per-lane fault and completion/failure state |

## 10. Output Contract: Memory Trace Schema

Trace records must include:

- identity: kernel ID, core/CU, simt_group_id, PC, sequence ID.
- access: op, address space, active lane mask, per-lane address or coalesced segment, byte mask, width.
- data: store data, load response, destination register/lane map.
- state: outstanding tag/source ID, cache hit/miss, MSHR, bank, queue, replay/fault reason.
- ordering: fence/atomic scope, visibility event, response ordering.
- completion: writeback mask, store commit, fault, scheduler release, latency/counter fields.

## 11. Verification Gate

| Gate | Required proof |
|---|---|
| M0 blocking | single-lane load/store trace matches oracle |
| mask/byte | partial lanes and mixed access widths preserve byte enables |
| vector lanes | per-lane address/data/writeback is traceable |
| outstanding | tag/source checker catches reuse and routes out-of-order responses |
| coalescing | coalesced result matches uncoalesced oracle and records merge/split rate |
| cache/MSHR | hit, miss, full, fill, and replay states are covered |
| ordering | fence/atomic/flush tests prove visibility and dependency rules |
| GPGPU-Sim alignment | behavioral evidence matches semantic contract where used as oracle/reference |

## 12. Design Evidence Layer

Use references only as evidence:

| Evidence | Use |
|---|---|
| GPGPU-Sim | behavioral evidence for LSU lifecycle, `mem_fetch`-like context preservation, cache/MSHR/DRAM stats |
| Rocket Chip | structural reference for explicit request/response schemas, source ID lifetime, monitors/fuzzers |
| Vortex/MIAOW | implementation anchors for GPU LSU, coalescer, memory-unit, trace and FPGA memory paths |
| XiangShan | tradeoff justification for replay cause priority, LSQ lifecycle, vector metadata, counter attribution |
| golden sim | semantic oracle for uncoalesced memory effects and ordering |

Evidence validates memory contracts; it must not structure the skill as cache/LSU/framework chapters.

## 13. Failure Modes

- Cache is added before a traceable blocking LSU exists.
- Tag/source ID is reused before all responses retire.
- Coalescer drops per-lane byte enable, destination, or fault metadata.
- Store completion is confused with response acceptance.
- Fence/flush only changes test code, not memory visibility state.
- Memory stalls are counted generically after adding distinct hazards.
