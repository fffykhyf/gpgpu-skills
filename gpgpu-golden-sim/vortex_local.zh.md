# GPGPU Golden Simulation 的 Vortex 本地参考

本文件展开 `gpgpu-golden-sim` skill 需要的 Vortex 参考，覆盖 SimX 模块组织、trace schema、memory payload、LSU golden model 和 first-divergence 工作流。目标是让日常 simulator、trace、RTL 对比工作不必每次重新通读 Vortex。

## 这个 skill 应该从 Vortex 学什么

Vortex 把 SimX 当作硬件的模块化可执行 twin，而不是单个中心解释器。simulator 拥有和 RTL 类似的概念：scheduler、decode、scoreboard、operands、dispatch、functional units、LSU、coalescer、caches、local memory、CTA dispatch 和 runtime launch state。

本地项目应该复制这些纪律：

- RTL 行为实现前先定义 architecture effect；
- simulator 行为放在拥有对应 timing/module behavior 的 owner 附近；
- trace identity 要足够映射回 RTL 事件；
- 比较 first divergence 时先看 architectural effect，再看 timing；
- 不要为了匹配可疑 RTL waveform 直接修改 simulator。

## 参考阅读顺序

| Path | 关注点 |
|---|---|
| `ref/skillref/vortex.md` | SimX as oracle、trace-first debug、staged memory、runtime/config/PPA 分层。 |
| `ref_submodule/vortex/docs/simulation.md` | 同一 workload 如何通过 `simx`、`rtlsim` 和其他 backend 运行。 |
| `ref_submodule/vortex/docs/debugging.md` | `run.log`、trace flags、`trace_csv.py`、UUID sorting、SimX-vs-RTL comparison。 |
| `ref_submodule/vortex/docs/designs/simx_simulator_architecture.md` | 无中央 Emulator、`SimObject` timing object、backpressured channel、module twin。 |
| `ref_submodule/vortex/docs/testing.md` | regression tests 和 runtime-facing tests 如何接入 simulator/runtime flow。 |

## SimX 拓扑

`ref_submodule/vortex/sim/simx/core.cpp` 是理解 Vortex golden simulator 结构的最佳单文件参考。`Core::Impl` 构造了一个 mirror RTL pipeline 的 simulator object graph：

- `Scheduler` 拥有 warp selection、PC、active masks、CTA activation、barrier state、warp suspend/resume。
- `Decoder` 和 optional `Decompressor` 把 fetched instruction words 转成 decoded instruction objects。
- `Scoreboard` 单独跟踪 hazards，而不是把 hazard 藏在 operand fetch 或 execution 中。
- per-warp `Sequencer` 建模 fetch/decode sequencing。
- per-issue `Operands` 读取 source registers。
- per-FU `Dispatcher` 把 issue slots 路由到 ALU、FPU、LSU、SFU、TCU。
- `AluUnit`、`FpuUnit`、`LsuUnit`、`SfuUnit`、optional `TcuUnit` 拥有各自 instruction semantics。
- memory path 不藏在 core loop 里：`LocalMem`、`LocalMemSwitch`、`MemCoalescer`、`LsuMemAdapter`、optional `Mmu` 和 cache ports 都是独立对象。

本地规则：golden simulator 要按 ownership 可 debug。如果 bug 在 scoreboard wakeup，simulator 应该有 scoreboard owner；如果 bug 在 LSU response demux，simulator 应该有 LSU/memory owner。单个 `execute_instruction()` 可以作为最早期原型，但不应该成为 RTL timing/trace alignment 的长期 oracle。

## Scheduler 与 Warp State

`ref_submodule/vortex/sim/simx/scheduler.cpp` 是 SIMT control state 的关键模型。

重要细节：

- `warp_t` 保存 `tmask`、`PC`、per-warp `uuid`、`mscratch`、floating/control CSRs 和 CTA CSRs；register file 在其他 owner 中。
- `Scheduler::activate_warp()` 把 CTA metadata 装入 warp：CTA id/rank/size、thread/block/grid dimensions、kernel entry、local-memory address、cluster size、argument pointer (`mscratch`)。
- 复用 CTA warp 时可以跳过一次性 prologue，把 PC rewind 到固定 per-CTA dispatch window。这是 runtime/kernel-entry 细节，但会影响 simulator scheduler。
- `schedule()` 先让 CTA dispatcher 激活一个 warp，再处理 pending `wspawn`，再选择 active、non-stalled、被 mask 允许的 warp。
- 新 `instr_trace_t` 在 fetch/decode 填充更多信息前先获得 `uuid`、`cid`、`wid`、`cta_id`、`PC`、`tmask`。
- `suspend()` 和 `resume()` 更新 registered next-state (`stalled_warps_next_`)，避免同周期 resume 的 warp 又被重新 schedule。

本地 simulator 即使策略更简单，也要保留这些显式状态类别：active warps、stalled warps、PC、active mask、CTA/kernel state、trace identity。

## Instruction Trace Schema

`ref_submodule/vortex/sim/simx/instr_trace.h` 是最有用的 trace schema 参考。`instr_trace_t` 携带足够上下文，把 fetch、decode、issue、FU、memory、writeback 串起来。

值得保留的字段类别：

- identity：`uuid`、`cid`、`wid`、`cta_id`
- control：`tmask`、`PC`、raw `code`、decoded instruction pointer
- writeback：`wb`、`dst_reg`、`dst_data`、`dst_bytesel`
- operands：`src_regs`、`src_data`
- execution class：`fu_type`、`op_type`
- packet/timing：`pid`、`sop`、`eop`、`num_pkts`、`issue_time`
- scheduler/debug：`fetch_stall`、`resume_warp`

`operator<<` 会打印 core/warp/CTA、mask、PC、writeback、destination/source registers、execution type、packet markers 和 UUID。这就是能和 RTL 对比的 trace 最小形状。

不要照搬 Vortex 字段名。保留类别即可：identity、control、operands、execution class、writeback、memory、scheduling reason。只有在能帮助定位 first divergence 时才加字段。

## Memory Trace Payloads

`ref_submodule/vortex/sim/simx/types.h` 定义 SimX 的 memory event payload：

- `MemReq`：operation、address、optional data block、byte enable、tag、hart id、UUID、flags，并提供 read/write 和 address type helper。
- `MemRsp`：tag、hart id、UUID、optional data block。

memory 正确性不是只看最终 memory contents。有用的 memory trace 要保留 lane mask、byte enable、原始 SIMT context、request tag、response ordering、writeback destination。只记录 `load addr -> value` 很难 debug coalescing、partial response 或 divergent warp memory。

## LSU Model 作为 Golden Reference

`ref_submodule/vortex/sim/simx/lsu_unit.cpp` 是 unit-level golden model 的好例子，比纯 ISA interpreter 更详细。

关键行为：

- `compute_addrs()` 根据 decoded operands 和 instruction args 生成 per-thread address/size/data list，并尊重 active mask。
- `ingest_inputs()` 让 request queue 成为真实的一周期 stage；while-loop 会伪造 bandwidth 并隐藏 timing bug。
- fence 会等待 older per-block requests drain；这是 ordering model，不是 no-op。
- `process_request_step()` 每次发一个 memory-side batch，为 loads/AMOs 分配 pending entry，保存 lane metadata，并跟踪是否 EOP。
- `process_response_step()` 用 response tag 找回 pending entry，格式化 signed/unsigned/float load data，应用 byte-selection 和 NaN-boxing，只在 terminal response 到达时 forward 到 writeback。
- loads、stores、load latency 等 perf counters 在行为 owner 附近更新。

本地规则：如果 RTL LSU 支持 outstanding requests，simulator 必须有显式 pending table 或等价、可 trace 的 routing state。

## First-Divergence 工作流

Vortex 的 debugging docs 和 `ci/trace_csv.py` 支撑以下流程：

1. 用同一个 workload、backend config、input memory、launch shape 跑 golden simulator 和被测实现。
2. 尽量用稳定 instruction/memory UUID 输出 trace。
3. 把 noisy log 转成可比较 row；`trace_csv.py` 是参考。
4. 先比较 committed architectural effects：PC、active mask、destination register、writeback data、memory write、exception/termination。
5. architectural effects 匹配后再比较 timing：stall reason、issue cycle、cache latency、queue occupancy。
6. 把 first mismatch 分类为 simulator bug、RTL bug、runtime/launch bug、memory model bug 或 test harness mismatch。

## 本地迁移清单

- 每个非平凡 RTL module 都要映射到 simulator owner，或明确说明暂不建模。
- simulator 和 RTL 的 trace identity 要稳定；UUID 最理想，早期可用 deterministic sequence id。
- memory request 必须自描述：op、address、mask、byte enable、data、tag、destination、SIMT context。
- instruction semantics 靠近 modeled unit，不要把 LSU/barrier/scheduler 行为塞进 generic interpreter。
- 修改 RTL 或 simulator 之前先给出 first-divergence report。
- bring-up 时先稳定 functional trace，再按具体 debug 问题加入 timing fields。

## 不要照搬的内容

- 不要在小项目里引入所有 Vortex simulator object。
- architectural trace 尚未稳定前，不要要求 cycle-exact agreement。
- 不要无理由采用 Vortex queue size、cache size 或 extension behavior。
- 不要让 trace format 无目的膨胀。
