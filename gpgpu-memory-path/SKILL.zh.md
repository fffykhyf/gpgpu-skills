---
name: gpgpu-memory-path
description: 用于设计、修改或调试 GPGPU memory behavior，包括 LSU frontend/backend、lane masks、byte enables、outstanding requests、response demux、stores、loads、coalescing、banking、cache、MSHR、fences、stalls 或 memory traces。
---

# GPGPU Memory State Machine Skill

## 1. Objective

把 memory 实现成 address spaces、lane masks、cache/coalescer state、outstanding requests、ordering 和 responses 上的 state machine，而不是 LSU/cache/NoC 子系统列表。

## 2. Input Contract

输入是 memory behavior intent，必须包含 issue packet schema、config digest、address spaces、mask/byte rules、ordering/fence requirements、cache/coalescer scope 和 oracle alignment target。

## 3. Memory State Model

| State | Fields |
|---|---|
| address space state | global、shared/LDS、local、constant、MMIO/uncached、cacheability、translation/fault status |
| coherence/visibility state | host/device visibility、fence scope、flush state、atomic serialization、cache ownership |
| cache line state | tag、valid/dirty、sector bits、MSHR ownership、fill/evict state |
| outstanding request table | tag/source ID、simt_group_id、PC、op、lane mask、byte mask、destination、response route |
| coalescer state | per-lane address groups、segment merge、split requests、partial response mapping |
| pipeline state | issue、coalesce、tag lookup、miss/refill、response、retire/replay |
| hazard state | bank conflict、miss、queue full、ordering wait、replay/nack、fault、deadlock watchdog |

## 4. 固定五问

每个 memory change 必须回答：

1. What state exists? 指明 address、cache、outstanding、coalescer、ordering 或 pipeline state。
2. Who produces it? LSU、coalescer、cache、interconnect、DRAM、response demux 或 runtime fence。
3. Who consumes it? SIMT scheduler、register writeback、cache、runtime、oracle、trace 或 PPA。
4. How does it change? 定义 issue、merge、miss、fill、response、replay、fence、flush、fault transitions。
5. How do we verify it? 指明 memory trace、monitor、oracle alignment、directed test 或 counter check。

## 5. Access Contract

每个 access 必须携带：

- kernel ID、compute core/CU ID、simt_group_id、PC 或 instruction ID。
- op：load、store、atomic、fence、flush、prefetch 或 unsupported。
- address space 和 cacheability。
- active lane mask、per-lane address、byte enable、width、alignment。
- store data 或 destination register mapping。
- tag/source ID 和 response route。
- ordering scope 和 fence/atomic semantics。
- fault/replay/kill eligibility。

## 6. Warp Coalescing Rule

Coalescing 是从 lane accesses 到 one or more memory transactions 的 transformation：

```text
lane requests + active mask -> segment groups -> memory transactions -> partial responses -> per-lane writeback/fault
```

- Semantic result 必须匹配 uncoalesced per-lane execution。
- Coalesced transactions 必须保留 byte enables、lane ownership、destination mapping、fault metadata。
- Partial responses 只能 retire 覆盖到的 lanes。
- Replays 必须恢复 lane ownership，不能重复 store 或丢 load destination。

## 7. Transformation Rules: Memory Pipeline

```text
issue -> coalesce -> tag -> miss -> fill -> retire
```

| Stage | Input state | Transformation | Output state |
|---|---|---|---|
| issue | SIMT issue packet | validate op、masks、address space、alignment | memory request candidate |
| coalesce | per-lane requests | group/split lanes into transactions | transaction list and lane map |
| tag | transaction | allocate outstanding entry/source ID | in-flight request |
| miss | cache/bank/interconnect state | hit、miss、queue、replay、bank conflict、fault | response wait or replay |
| fill | downstream response | update cache/MSHR/outstanding table | response payload |
| retire | response payload | write back loads、commit stores/atomics、clear waits | memory trace and scheduler release |

Blocking LSU 也使用同一 stages，只允许一个 in-flight request。

## 8. Hazard Model

| Hazard | Required rule |
|---|---|
| bank conflict | conflict detection、stall/replay priority、counter owner |
| cache miss | MSHR allocation、miss queue full behavior、fill ownership |
| response ordering | in-order/out-of-order rule、tag lifetime、demux assertion |
| memory dependency | load/store/atomic/fence ordering scope 和 scoreboard interaction |
| queue pressure | full conditions、backpressure path、no-drop assertion |
| replay/nack | replay cause enum、priority、state restoration、deadlock proof |
| fault | address/access fault state、per-lane reporting、completion semantics |
| flush/kill | outstanding request behavior、response ignore 或 drain rule |

多个 hazard 可同时为真时，必须定义 priority 和 trace field。

## 9. State Evolution

| Event | State change |
|---|---|
| LSU accepts issue packet | capture PC、mask、op、address metadata、destination |
| address generation | produce per-lane addresses and byte masks |
| coalescer accepts | allocate lane-to-transaction map |
| tag allocation | create outstanding request entry and block dependent SIMT group |
| cache hit | return response 或 store commit through retire stage |
| cache miss/MSHR allocate | track fill state and downstream route |
| replay/nack/full | preserve request and release/retry by priority |
| response arrives | demux by tag/source to SIMT group、lane mask、destination |
| retire | update register file 或 store visibility，clear memory wait |
| fence/flush | update ordering/coherence state and runtime visibility |
| fault | record per-lane fault and completion/failure state |

## 10. Output Contract: Memory Trace Schema

Trace records 必须包含 identity、access、data、state、ordering、completion：

- identity：kernel ID、core/CU、simt_group_id、PC、sequence ID。
- access：op、address space、active lane mask、per-lane address/coalesced segment、byte mask、width。
- data：store data、load response、destination register/lane map。
- state：outstanding tag/source ID、cache hit/miss、MSHR、bank、queue、replay/fault reason。
- ordering：fence/atomic scope、visibility event、response ordering。
- completion：writeback mask、store commit、fault、scheduler release、latency/counter fields。

## 11. Verification Gate

| Gate | Required proof |
|---|---|
| M0 blocking | single-lane load/store trace matches oracle |
| mask/byte | partial lanes 和 mixed access widths 保留 byte enables |
| vector lanes | per-lane address/data/writeback traceable |
| outstanding | tag/source checker 捕捉 reuse 并 route out-of-order responses |
| coalescing | coalesced result matches uncoalesced oracle，并记录 merge/split rate |
| cache/MSHR | hit、miss、full、fill、replay states covered |
| ordering | fence/atomic/flush tests 证明 visibility/dependency rules |
| GPGPU-Sim alignment | 作为 oracle/reference 时 behavioral evidence 匹配 semantic contract |

## 12. Design Evidence Layer

| Evidence | Use |
|---|---|
| GPGPU-Sim | LSU lifecycle、`mem_fetch` context preservation、cache/MSHR/DRAM stats 的 behavioral evidence |
| Rocket Chip | request/response schemas、source ID lifetime、monitors/fuzzers 的 structural reference |
| Vortex/MIAOW | GPU LSU、coalescer、memory-unit、trace/FPGA memory paths 的 implementation anchors |
| XiangShan | replay cause priority、LSQ lifecycle、vector metadata、counter attribution 的 tradeoff justification |
| golden sim | uncoalesced memory effects 和 ordering 的 semantic oracle |

Evidence 验证 memory contract；不能把 skill 组织成 cache/LSU/framework chapters。

## 13. Failure Modes

- cache 在 traceable blocking LSU 前加入。
- tag/source ID 在所有 response retire 前复用。
- coalescer 丢 per-lane byte enable、destination 或 fault metadata。
- store completion 与 response acceptance 混淆。
- fence/flush 只改 test code，不改变 memory visibility state。
- 添加 distinct hazards 后仍只计一个 generic memory stall。
