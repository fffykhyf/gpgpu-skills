# GPGPU Memory Path 的 Vortex 本地参考

本文件展开 `gpgpu-memory-path` skill 需要的 Vortex 参考，重点是 LSU frontend/backend separation、lane mask、byte enable、tag、coalescing、cache、fence、VM，以及 simulator/RTL trace alignment。

## 这个 skill 应该从 Vortex 学什么

Vortex 不把 memory 当作黑盒 load/store function。它把 memory path 分成 ownership 清晰的层：

- LSU frontend：AGU、address classification、byte enable、store data alignment、fence lock、response formatting。
- Memory scheduler/backend：request queue、load index buffer、optional coalescer、batching、response demux、watchdogs。
- Cache/bank/memory layer：bank selection、merge/response crossbar、MSHR、flush、local memory、MMU、deadlock prevention。
- Simulator mirror：LSU unit、local-memory switch、coalescer、cache adapters、memory request/response payloads、counters。

本地项目应该复制 staged discipline：先做 traceable blocking path，再在 trace 能证明正确性后添加 outstanding loads、coalescing、cache、VM。

## 参考阅读顺序

| Path | 关注点 |
|---|---|
| `ref/skillref/vortex.md` | staged memory-path lessons。 |
| `ref_submodule/vortex/docs/designs/lsu_pipeline_design.md` | LSU frontend/backend、response demux 规则。 |
| `ref_submodule/vortex/docs/cache_subsystem.md` | cache bank dispatch、merge crossbar、MSHR、flush、deadlock。 |
| `ref_submodule/vortex/docs/designs/simx_simulator_architecture.md` | SimX memory graph：LSU、coalescer、local memory、cache、DRAM、`MemReq`、`MemRsp`。 |
| `ref_submodule/vortex/docs/hardware_library.md` | elastic buffers、arbiters、allocators、counters、flow-control modules。 |
| `ref_submodule/vortex/VX_config.toml` | LSU lanes、queue sizes、cache sizes/ways/MSHR、memory block size、local memory settings。 |
| `ref_submodule/vortex/VX_types.toml` | memory map、local memory map、cache/memory/TLB/PTW counters。 |

## RTL LSU Frontend

`ref_submodule/vortex/hw/rtl/core/VX_lsu_slice.sv` 是最具体的 frontend 参考。

重要行为：

- AGU 计算 per-lane `full_addr = rs1 + offset`。
- address attributes 按 lane 计算并作为 sideband 传递：IO address、local memory address、flush/fence、optional AMO metadata。
- AMO request 携带 operation、signed/unsigned flavor、packed hart id。atomic extension 关闭时 sideband 被 tie off，避免 unknown 传播。
- store/load width 转成 byte-enable mask；8/16/32/64-bit access 根据低位地址移动 byte-enable。
- store data 根据 byte-enable lane 做 shift/alignment。
- simulation 中显式 assert misaligned memory access。
- fence 使用 `fence_lock`，直到对应 response unlock 前阻止新 memory request。
- store-without-response 和 skipped fence packet 通过 no-response result buffer，让 commit/writeback ordering 保持一致。
- request tag 打包 instruction header、op type、per-lane alignment、packet index、fence bit。response formatter 用它恢复 destination 和 packet metadata。
- load response formatting 负责 sign/zero extend byte/half/word data，处理 RV64/F32 NaN-boxing，恢复 response mask，转发 SOP/EOP packet markers。

本地规则：memory request 必须携带足够原始 SIMT metadata，不能靠 response order 猜 writeback。

## Multi-Packet 与 PID Tracking

`VX_lsu_slice.sv` 还展示了一个 warp request 被拆成多个 memory packet 时如何跟踪 packetized load。

当 `PID_BITS != 0` 时，frontend 保存：

- packet allocator；
- per-packet counters；
- SOP/EOP flags；
- request 和 response 触碰同一 packet entry 的 collision case；
- allocator full 和 broken SOP sequence 的 assertions。

如果本地设计支持 vector-lane memory、coalesced line request 或任何 out-of-order response path，这很有参考价值。关键不是照搬 counter，而是 SOP/EOP 在 request split 后不能从最后一个 response 推断。

## Memory Scheduler Backend

`ref_submodule/vortex/hw/rtl/libs/VX_mem_scheduler.sv` 是 generic backend 参考。它由 core request lanes、memory channels、word/line size、tag width、queue sizes、partial response mode、output buffering 等参数化。

重要组成：

- request queue 在检查 load index-buffer 空间后保存 core requests。
- loads 分配 index-buffer entry；stores 不需要 return entry。
- outgoing memory tag 组合 UUID bits、index-buffer address、batch index；response tag 用于恢复原始 core tag。
- optional `VX_mem_coalescer` 在 line size 大于 word size 时合并多个 word requests。
- 大 merged request 跨 memory channels 分批发出，batch index 进入 memory tag。
- response 可以 partial return (`RSP_PARTIAL`)，也可以存储 piece 直到 request 所有 lane 完成。
- remaining-mask table 跟踪 multi-lane request 哪些 lane 仍等待 response。
- simulation watchdog 捕获永远没有 response 的 request。
- debug trace 包含 core request、memory request、memory response、core response、tags、UUIDs。

本地 memory work 不要在没有 index-buffer/tag/release 方案时引入 out-of-order responses；不要在不能保留 per-lane byte enable 和 response reconstruction 时引入 coalescing。

## Core Memory Unit 与 Cache Layer

`ref_submodule/vortex/hw/rtl/core/VX_mem_unit.sv`、`ref_submodule/vortex/hw/rtl/cache/`、`ref_submodule/vortex/hw/rtl/mem/` 是 downstream 参考。

初读时优先看文档：

- `docs/cache_subsystem.md`：bank dispatch、response merge、MSHR、flush、deadlock。
- `docs/hardware_library.md`：elastic buffers、arbiters、allocators、counters。
- `VX_config.toml`：`VX_CFG_MEM_BLOCK_SIZE`、`VX_CFG_NUM_LSU_LANES`、`VX_CFG_LSU_LINE_SIZE`、`VX_CFG_LSUQ_IN_SIZE`、`VX_CFG_LSUQ_OUT_SIZE`、cache sizes、ways、MSHR sizes、bank counts、local memory log size、TLB size。

如果本地项目仍在 blocking LSU 阶段，这些应作为后续阶段参考。cache 和 MSHR 不是正确 memory contract 的前提。

## Simulator Memory Mirror

`ref_submodule/vortex/sim/simx/core.cpp` 构造 SimX memory graph：

- per-LSU-block `MemCoalescer`；
- `LocalMem`；
- `LocalMemSwitch`；
- dcache/local-memory adapters；
- optional per-core dcache/icache `Mmu`；
- core cache ports。

constructor 显式绑定 local-memory 和 dcache path。local memory enable 时，access 可经 `LocalMemSwitch`；VM enable 时，dcache request 先过 MMU 再到 cache hierarchy。

`ref_submodule/vortex/sim/simx/types.h` 定义：

- `MemReq`：operation、address、data block、byte enable、tag、hart id、UUID、flags。
- `MemRsp`：tag、hart id、UUID、optional data block。

这些是本地 trace template。golden memory trace 应暴露 op、address、byte enable、tag、response、SIMT context，而不只是 `addr -> data`。

## SimX LSU Unit

`ref_submodule/vortex/sim/simx/lsu_unit.cpp` 是 RTL LSU path 的 simulator counterpart。

相关行为：

- `compute_addrs()` 根据 decoded operands 和 active mask 构造 per-thread address/size/data list。普通 LSU uop 使用 `rs1 + stride * rs2 + offset`，AMO 作为单独 typed operation。
- `ingest_inputs()` 每周期最多把一个 trace 放入 request queue，保留真实 queue stage。
- queue head 的 fence 等待 older per-block requests drain。
- `process_request_step()` 每周期最多发一个 memory-side batch，为 loads/AMOs 分配 pending entries，保存 lane metadata，保留 original thread id，设置 UUID/core id，发出 `LsuReq`。
- `process_response_step()` 消费一个 response packet，用 tag 找 pending entry，格式化 load data，处理 byte selection 和 NaN-boxing，只在 terminal response 时 forward trace。
- `pending_loads_` 驱动 load-latency counters。

本地 memory golden simulator 应该有可 trace 的 pending state，而不是 direct load/store。

## Counters 与 Debug Signals

`ref_submodule/vortex/VX_types.toml` 给出有用 counter 分类：

- core-level LSU：loads、load latency、stores；
- cache：reads/writes、read/write misses、evictions、bank stalls、MSHR stalls；
- memory：reads、writes、memory latency、bank stalls；
- local memory：reads/writes、bank stalls；
- coalescer misses；
- TLB lookups/hits/misses/evictions、PTW walks/latency。

memory optimization 需要 trace 证明正确，也需要 counter 说明 bottleneck 改变。

## 本地阶段计划

| Stage | Capability | Required proof |
|---|---|---|
| M0 | blocking scalar load/store | address、width、byte-enable、data trace 正确 |
| M1 | active lane mask 和 partial width | divergent lanes 和 subword tests pass |
| M2 | vector-lane memory | per-lane address/data/mask 可 trace |
| M3 | outstanding loads | tag/index-buffer 能路由 out-of-order responses |
| M4 | coalescing | merge/miss/partial-response behavior 可观察 |
| M5 | cache/bank/MSHR | hit/miss/full/bank/deadlock tests 存在 |
| M6 | fence/flush/VM | ordering 和 translation contracts 明确 |

## 不要照搬的内容

- blocking LSU contract 尚不可 trace 时，不要加 cache/MSHR/VM。
- 引入 outstanding loads 后，不要假设 in-order response。
- coalescing 不能丢 lane metadata。
- 不要无本地 PPA 证据照搬 Vortex queue depth 或 cache size。
- 不要把最终 kernel output 当作唯一 memory correctness signal。
