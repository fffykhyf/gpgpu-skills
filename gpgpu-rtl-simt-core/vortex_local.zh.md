# RTL SIMT Core 的 Vortex 本地参考

本文件展开 `gpgpu-rtl-simt-core` skill 需要的 Vortex 参考，重点是 SIMT core state、RTL pipeline boundary、scheduler/issue/writeback 行为，以及让 RTL debug 可落地的 simulator mirror。

## 这个 skill 应该从 Vortex 学什么

Vortex 把 SIMT 状态显式化。warp PC、active mask、active/stalled warp sets、packet markers、scoreboard reservations、CTA state、writeback release rules 都不是临时 wire，而是 RTL、simulator 和 trace 中都应该可见的 contract。

本地项目要迁移这些习惯：

- 改 scheduler 前先定义 warp lifecycle；
- schedule、fetch、decode、issue、operands、dispatch、execute、commit 的职责要可分；
- scoreboard ownership 不应藏进 operand read side effect；
- branch/divergence/barrier/CTA state 要可观察；
- 依赖 simulator trace 对齐，不只靠 waveform。

## 参考阅读顺序

| Path | 关注点 |
|---|---|
| `ref/skillref/vortex.md` | SIMT lesson 如何映射到本地 skill。 |
| `ref_submodule/vortex/docs/microarchitecture.md` | threads、warps、active masks、`TMC`、`WSPAWN`、`SPLIT`、`JOIN`、`PRED`、`BAR`、pipeline。 |
| `ref_submodule/vortex/docs/designs/cta_clustering_and_dispatch.md` | CTA-to-warp dispatch、CTA rank/size、cluster dimensions、scheduler-visible launch state。 |
| `ref_submodule/vortex/docs/designs/simx_simulator_architecture.md` | scheduler、decoder、scoreboard、operands、dispatcher、functional units 的 simulator mirror。 |
| `ref_submodule/vortex/docs/debugging.md` | trace-first RTL debug 和 SimX/RTL comparison。 |

## RTL Core 顶层边界

`ref_submodule/vortex/hw/rtl/core/VX_core.sv` 是 top-level RTL 参考。它把 core pipeline 连接起来，并把 core 对外 contract 暴露给 GPU 其他部分。

需要注意的边界：

- core identity 和配置来自参数或 generated macros，不是隐藏常量；
- instruction fetch 和 data memory 通过显式 memory/cache/MMU-facing interfaces；
- CTA dispatch 和 scheduler state 在命名 interface 处相遇，而不是 testbench-only launch poke；
- LSU、FPU、SFU、TCU、ALU 是 dispatch 后的独立 execute paths；
- performance counters 和 debug trace 靠近实际 pipeline event。

小 core 可以合并模块，但不要合并 contract。设计必须能回答：谁拥有 PC、谁拥有 active mask、谁能 stall warp、谁 reserve writeback、谁 release writeback。

## Scheduler 与 Warp Lifecycle

`ref_submodule/vortex/hw/rtl/core/VX_scheduler.sv` 和 SimX mirror `ref_submodule/vortex/sim/simx/scheduler.cpp` 展示同一核心思想。

值得复制的状态类别：

- active warp set；
- stalled/waiting warp set；
- per-warp PC；
- per-warp active mask；
- per-warp CTA/kernel state；
- branch/divergence/reconvergence state；
- barrier 或 CTA completion state；
- suspend/resume 的 next-state update rule。

SimX `Scheduler::schedule()` 是正确 sequencing 的简洁参考：CTA dispatch 可以激活 warp，`wspawn` 可以添加 warp，ready warp 被选择，trace identity 被分配，然后 warp 被 suspend，直到后续 pipeline stage resume。这个分离避免同周期 release 的 warp 被重复 issue。

本地 RTL 改 scheduler 前先写清 lifecycle：inactive、ready、issued/waiting、waiting on scoreboard/operands/FU/memory、barrier-stalled、CTA-reused、done。缺失状态通常会变成 valid-ready 隐式 bug。

## Fetch、Decode、Issue、Commit 形状

Vortex 保留常见 SIMT pipeline stage：

- `VX_fetch.sv`：instruction request path 和 per-warp fetch state。
- `VX_decode.sv`：raw instruction 到 decoded control。
- `VX_issue.sv`：decoded instruction buffering、slot selection、hazard checks、dispatch eligibility。
- `VX_execute.sv`：路由到 functional units。
- `VX_commit.sv`：接收 unit results、仲裁 writeback、release scoreboard、更新 PC/control side effects、输出 debug trace。

skill-level 规则：这些职责不要藏在一个大 always block。小项目可以少文件，但 trace 和注释应该保留这些概念阶段。

## Issue Slice 与 Scoreboard 细节

`ref_submodule/vortex/hw/rtl/core/VX_issue_slice.sv` 是 slice-level composition 参考。它连接：

- `VX_ibuffer`：decoded instruction buffering；
- `VX_scoreboard`：dependency 和 structural hazard checks；
- `VX_operands`：register operand reads；
- `VX_dispatcher`：把 issue packet 送到 selected FU。

slice 暴露 `warp_issued`，debug/scope 下 tap decode、operands、writeback events。正确心智模型是：issue 不只是 valid-ready 传输，也是 stall attribution 应该可见的地方。

`ref_submodule/vortex/hw/rtl/core/VX_scoreboard.sv` 是 hazard 参考。重要行为：

- 按 warp 跟踪 in-use integer/floating/vector destination registers；
- instruction 离开 staging 时 reserve writeback destinations；
- writeback 时 release reservation，并用 EOP 避免 multi-packet instruction 过早释放；
- busy source/destination 会阻塞；
- 建模 FU locks/blocks，并用 arbitration 做 issue selection；
- simulation assertion 捕获 invalid writeback 和 timeout-like bugs；
- 输出 performance stall 信息。

本地 RTL 要先定义：destination 何时 reserve、何时 free、multi-packet operation 在 SOP 还是 EOP free、flush/kill/reset 如何影响 outstanding reservations。做完这些再加 issue width。

## SIMT Control：Split/Join、TMC、WSPAWN、Barrier

Vortex microarchitecture docs 描述这些 SIMT control instructions：

- `TMC` 修改 active thread mask。
- `WSPAWN` 在目标 PC 激活更多 warps。
- `SPLIT` 和 `JOIN` 维护 divergent branch/reconvergence state。
- `PRED` 处理 predicate-like mask behavior。
- `BAR` 和 barrier unit / warp scheduler 交互。

相关 RTL：

- `ref_submodule/vortex/hw/rtl/core/VX_split_join.sv`
- `ref_submodule/vortex/hw/rtl/core/VX_ipdom_stack.sv`
- `ref_submodule/vortex/hw/rtl/core/VX_wctl_unit.sv`
- `ref_submodule/vortex/hw/rtl/core/VX_bar_unit.sv`

不要把 divergence 当成 branch 的隐藏 side effect。本地设计需要明确 active-mask update、reconvergence target、stack push/pop、warp wakeup 的 owner。简化实现也要写清缺失 case，而不是留下 unspecified behavior。

## CTA Dispatch 与 KMU 边界

Vortex 的 launch path 通过 KMU/CTA boundary 到 core：

- `ref_submodule/vortex/hw/rtl/VX_kmu.sv` 拥有来自 DCR 的 kernel-management state：startup PC、kernel entry、args pointer、grid/block dimensions、local memory size、block size、warp step、cluster dimensions。
- `ref_submodule/vortex/hw/rtl/core/VX_cta_dispatch.sv` 向 core scheduler 提供 warp records，包括 CTA id/rank/size、thread/block indices、per-CTA entry/argument state。
- SimX 在 `sim/simx/scheduler.cpp` 中 mirror：`activate_warp()` 把 CTA metadata 复制进 warp-visible CSR state。

CTA state 不是 testbench 装饰。它影响 CSRs、per-thread IDs、local memory addressing、kernel entry、warp reuse。即使是 minimal runtime，也要保留这个边界。

## Commit 与 Writeback Contract

`ref_submodule/vortex/hw/rtl/core/VX_commit.sv` 是最终 architectural effect stage 的参考。通用 contract 是：

- 仲裁多个 functional unit 的 results；
- 只在 active mask 和 writeback enable 下写回；
- 保留 destination register type 和 byte-selection rules；
- 在 architectural completion point 更新 scoreboard release；
- 处理 branch/control instruction 的 PC/control side effects；
- 输出包含 PC、warp、mask、destination、data、FU/op type、SOP/EOP、UUID-like identity 的 trace row。

常见 bug 是 response packet 一到就 release scoreboard，而不是等 instruction architectural writeback 完成。

## Simulator Twin 参考

用这些 SimX 文件理解 RTL change 背后的 expected behavior：

- `ref_submodule/vortex/sim/simx/scheduler.cpp`：warp lifecycle、CTA activation、PC、active masks、suspend/resume。
- `ref_submodule/vortex/sim/simx/instr_trace.h`：trace identity 和字段。
- `ref_submodule/vortex/sim/simx/core.cpp`：module graph 和 core pipeline。
- `ref_submodule/vortex/sim/simx/scoreboard.cpp`：hazard ownership 的软件 mirror。
- `ref_submodule/vortex/sim/simx/operands.cpp`、`opc_unit.cpp`：operand 和 register-file semantics。
- `ref_submodule/vortex/sim/simx/*_unit.cpp`：functional unit semantics。

RTL 和 simulator 不一致时，先对齐 trace row。没有 scheduler/scoreboard/commit trace 的 waveform 通常更慢。

## 本地迁移清单

- 改 scheduler RTL 前列出 warp lifecycle states 和合法 transition。
- 添加 instruction 前列出它对 PC、active mask、scoreboard、register writeback、memory、barrier、CSR、CTA-visible state 的影响。
- 加 issue width 前定义 arbitration、FU locks、scoreboard conflicts、writeback conflicts。
- 加 divergence 前定义 reconvergence stack behavior 和 trace fields。
- 加 barrier 或 CTA dispatch 前定义 wakeup/completion semantics。
- 每个 RTL 行为变化都要更新或识别 simulator/golden trace owner。

## 不要照搬的内容

- 不要无目标导入 Vortex 完整 extension set。
- 小设计能保留 contract 时，不要照搬 Vortex pipeline depth。
- 不要把 scoreboard 行为实现进 operand read logic。
- 不要让 active mask 或 PC 变成临时 combinational helper。
- 没有可复现 trace 或 regression 时，不要只凭 waveform 宣称正确。
