---
name: gpgpu-memory-path
description: 用于设计、编辑或调试 GPGPU memory 行为，包括 LSU frontend/backend、lane masks、byte enables、outstanding requests、response demux、stores、loads、coalescing、banking、cache、MSHR、fences、stalls 或 memory traces。
---

# GPGPU Memory Path

## 概览

用于 LSU 和 memory-system 工作。先从 blocking、traceable path 开始；只有当 correctness traces 和 counters 能证明下一步有必要时，再加入 tags、response demux、coalescing、banking、cache、MSHR、fences 或 VM。使用 Rocket Chip 的 HellaCache、DCache 和 TileLink 作为 request/response schemas、source ID lifetime、replay/nack/kill semantics、ordering、protocol helpers、monitors 和 constrained fuzzing 的参考。使用 XiangShan 作为完整 LSU/LSQ/replay/cache/MMU/L2 lifecycle 的参考，尤其关注 replay-cause priority、violation handling、vector metadata 和 counter attribution。

## 核心规则

每个 memory request 都必须能通过 SIMT context 追踪：

- compute core/CU ID、simt_group_id、PC 或 instruction ID
- active lane mask
- per-lane address 或 coalesced address
- byte enable 和 access width
- store data 或 load response data
- destination register 或 request tag
- source ID 或 outstanding index lifetime
- response ordering rule
- relevant stall、nack、replay、kill、fence、flush 或 exception reason
- relevant address space、translation state 和 cacheability/MMIO classification
- 建模后还要记录 cache/memory status：hit、miss、reservation fail、MSHR full、queue full、ICNT full 或 DRAM wait

如果当前 trace 和 counters 不能展示某个 memory optimization 要解决的问题，就不要做该优化。

对于非平凡 memory path，还要在 trace 之外定义 protocol schema：op、size、address、byte mask、active lane mask、data、tag/source ID、ordering scope、cacheability、fault fields 和 response metadata。把它当成带 assertions 或 monitors 的 executable contract。

## 术语契约

Memory traces 和 tags 使用统一术语；只有命名 RTL 信号时保留源码别名。

| 统一术语 | 源码别名 | Memory-path 含义 |
|---|---|---|
| SIMT group | warp、wavefront、wave | 发出 memory operations 的 execution group |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | resident SIMT group 的 request/response identity |
| active lane mask | active mask、lane mask、thread mask、`EXEC` mask | 参与 load/store 的 lanes |
| CTA/workgroup | CTA、block、workgroup | local-memory 和 barrier scope |
| compute core/CU | core、CU、compute unit | memory-client owner |

## Frontend 和 Backend 拆分

| 区域 | 职责 |
|---|---|
| LSU frontend | AGU、address classification、byte enable、store-data alignment、fence lock、response formatting |
| Memory scheduler/backend | request queue、outstanding tag/index buffer、optional coalescing、batching、out-of-order response demux |
| Cache/bank layer | bank dispatch、hit/miss handling、MSHR、merge crossbar、flush、deadlock prevention |
| Protocol/check layer | source/tag validity、alignment、mask legality、ordering、replay/nack/fault、monitor/fuzzer hooks |

在 simulator、RTL、trace 和 tests 中保持这个拆分可见。

## GPGPU-Sim Memory Lifecycle

使用 GPGPU-Sim 作为 staged request path 的参考：

| 阶段 | GPGPU-Sim anchor | 本地规则 |
|---|---|---|
| issue to LSU | `ldst_unit` input pipeline | 捕获 SIMT group、PC、op、active lane mask、destination |
| space split | `shared_cycle`、`constant_cycle`、`texture_cycle`、`memory_cycle` | 在 cache behavior 之前先分类 memory space |
| request carrier | `mem_fetch` | 保留 SIMT context、tag、address、size、op、status 和 response route |
| L1/cache | `process_cache_access`、`gpu-cache` | 区分 hit、miss、hit-reserved、reservation fail、MSHR/miss-queue pressure |
| interconnect | `icnt_wrapper`、cluster injection | 暴露 routing 和 backpressure，不要假设 network 免费 |
| L2/partition | `memory_sub_partition` | 定义 L2 queues、sector split 和 DRAM admission |
| DRAM | `dram_t`、`dram_sched` | 定义 bank timing、scheduling、return queue |
| response | response FIFO、store ack、writeback | 按 tag demux 回 SIMT group、lane mask 和 destination |
| stats | memory latency/cache/DRAM stats | 做 optimization claim 前先测量 |

当设计超过 blocking LSU 后，不要把这些 owner 折叠成一个黑盒 memory model。

## Rocket Chip Memory Contract

使用 Rocket Chip 作为显式化 memory protocols 的参考：

| 契约 | Rocket Chip anchor | 本地规则 |
|---|---|---|
| request schema | `HellaCacheReq`、TileLink A/C channels | 显式携带 op、size、address、mask、data、tag/source ID、privilege/address-space，以及 no-response/no-allocate semantics。 |
| response schema | `HellaCacheResp`、TileLink D channel | 显式携带 data、replay、denied/fault、metadata、destination 和 source/sink identity。 |
| exceptional flow | DCache kill/nack/replay/flush/probe/release/grant | 说明 kill、flush、nack、replay、fence、fault、uncached/MMIO 和 outstanding requests 行为。 |
| derived helpers | `tilelink/Edges.scala` | 集中计算 beat、mask、first/last/done、source 和 address。 |
| executable checks | `tilelink/Monitor.scala`、`tilelink/Fuzzer.scala` | 在声明 protocol robustness 前加入 monitors 和 constrained random traffic。 |
| resource params | `DCacheParams`、MSHR/MMIO/source ID ranges | 在一个地方配置并检查 queue depths、MSHRs、MMIO slots 和 source/tag ranges。 |

把 TileLink 思路翻译成本地 GPGPU protocol；不要假设 CPU cache coherence protocol 就是 GPU memory model。

## XiangShan LSU Replay 模式

使用 XiangShan 作为 memory path 中 replay、violation 和 wakeup 都是一等设计对象的参考：

| Memory 契约 | XiangShan anchor | 本地 memory-path 规则 |
|---|---|---|
| backend-memory boundary | `MemBlock.scala` | 定义 issue、LSQ enqueue、commit、redirect、violation、exception、wakeup、writeback 和 perf ports。 |
| load/store queue owner | `LSQWrapper.scala` | 保持 load queue、store queue、bypass、forward、uncache、rollback、hint 和 debug ownership 显式。 |
| replay cause enum | `LoadQueueReplay.scala` | 枚举 replay reasons，并保留带 deadlock reasoning 的 priority ordering。 |
| vector metadata | `VecReplayInfo`、vector LSU files | 当存在 vector 或 lane replay 时，携带 per-element、mask、merge-buffer、offset 和 active metadata。 |
| cache/TLB path | `DCacheWrapper.scala`、`cache/mmu/` | 从 config 派生 source IDs、MSHR entries、TLB/PTW misses、uncache/MMIO、ECC 和 prefetch fields。 |
| shared L2/backpressure | PDF CoupledL2 章节、`L2Top.scala` | 文档化 MSHR、retry/credit、MMIO bridge、error 和 downstream protocol behavior。 |

本地 GPGPU memory 工作应命名 replay causes，例如 coalescer retry、shared-memory bank conflict、TLB miss、cache miss、MSHR full、NoC backpressure、atomic serialization、uncache/MMIO、fault 和 store/load ordering。若两个 cause 可同时为真，必须写出优先级并证明不会死锁。

第一版 blocking LSU 应命名自己的 FSM states，并 trace：

| 区域 | 必要证据 |
|---|---|
| issue capture | simt_group_id、PC、opcode、memory format、destination、SGPR/VGPR class |
| address generation | scalar base、vector offset、immediate、thread id、LDS base、global/LDS bit |
| lane control | active lane mask、skipped lanes、per-lane address vector |
| request | read/write enable、address、write data、write mask、tag |
| response | ack、tag、read data、destination register、writeback mask |
| completion | done simt_group_id、retire PC、memory wait release、trace event |

只有当该路径通过 load/store、masked-lane、global/LDS、SGPR/VGPR writeback 测试后，coalescing、cache、MSHR 或 VM 才应被当作实现工作，而不是推测。

## 阶段顺序

| 阶段 | 能力 | Gate |
|---|---|---|
| M0 | blocking scalar load/store | single-lane load/store trace 正确 |
| M1 | lane mask 和 byte enable | partial lane 和 access-width tests 通过 |
| M2 | vector lane memory | 每个 lane address、data、mask 都可追踪 |
| M3 | outstanding loads | tag 或 index buffer 能路由 out-of-order responses |
| M4 | coalescing | merge rate、replay、partial response 可解释 |
| M5 | bank/cache/MSHR/L2/ICNT | hit、miss、full queue、routing、deadlock tests 存在 |
| M6 | fence/flush/VM | ordering、translation、unsupported behavior 明确 |

只有当用户要求聚焦研究且缺失假设已文档化时，才能跳过阶段。

## Non-Blocking Load 要求

任何 non-blocking load 都必须说明：

- tag 或 index-buffer allocation 和 release。
- maximum outstanding requests。
- 每个 queue、coalescer、cache、interconnect 和 response 点上的 source ID 或 tag visibility。
- response demux 回到 SIMT group、lane mask 和 destination 的路径。
- flush、kill、fence、exception 或 queue-full 行为。
- 当对应层级存在时，说明 cache reservation failure、interconnect backpressure 和 response FIFO full 行为。
- 捕获 deadlock 的 watchdog、assertion 或 test。
- 针对 tag reuse、mask legality、alignment、replay 和 response completion 的 monitor 或 trace assertion。

## 常见错误

- 在 working blocking LSU 之前添加 cache。
- 引入 outstanding requests 后仍假设 in-order responses。
- 做 coalescing 时丢失 per-lane writeback、byte enables 和 exception behavior。
- 在 request tag 中丢掉原始 SIMT-group/lane/destination metadata。
- 添加 cache、interconnect、L2 或 DRAM queues 后仍只报告一个 generic memory stall。
- 把 final kernel output 当成唯一 memory correctness check。
- 在多个地方手写 beat/mask/source calculations，而不是集中派生 protocol helpers。
- 添加 replay、nack 或 out-of-order response support，却没有 source/tag lifetime checker。
- 添加 replay causes，却没有 XiangShan 风格的 priority table、owner counter 和 deadlock check。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 LSU scheduler、memory unit、coalescer/cache/MSHR boundaries 和 full-stack memory contracts。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 MIAOW LSU opcode decoder、address calculator、op-manager FSM、simple memory model、trace signals 和 limitations。

若想了解与本 skill 相关的 GPGPU-Sim 背景，请阅读本目录下的 `gpgpusim_local.md`。它说明 `ldst_unit`、`mem_fetch`、cache/MSHR status、L2/memory partitions、interconnect、DRAM timing、response routing 和 memory statistics。

若想了解与本 skill 相关的 Rocket Chip 背景，请阅读 `../../ref/skillref/rocket.md`，必要时查看 `../../ref_submodule/rocket-chip/src/main/scala/rocket/HellaCache.scala`、`rocket/DCache.scala`、`tilelink/Bundles.scala`、`tilelink/Edges.scala`、`tilelink/Monitor.scala`、`tilelink/Fuzzer.scala` 和 `diplomacy/Parameters.scala`。

若想了解与本 skill 相关的 XiangShan 背景，请阅读本目录下的 `xiangshan_local.md`。它说明 PDF 中的 LSU/DCache/MMU/CoupledL2 章节、`MemBlock`、`LSQWrapper`、`LoadQueueReplay`、DCache parameters、TLB/PTW structure、vector replay metadata，以及如何把这些细节适配到 GPGPU memory paths。
