---
name: gpgpu-arch-design
description: 用于规划、分阶段实现或评审 GPGPU 架构，范围包括 ISA、SIMT 执行、模拟器、RTL、runtime 启动、配置、测试、计数器、内存层级、PPA、FPGA bring-up 或路线图决策。
---

# GPGPU 架构设计

## 概览

将本 skill 作为本地 GPGPU 工作的顶层护栏。GPGPU 是完整系统工程，因此架构工作必须说明 ISA、模拟器、RTL、runtime、kernel ABI、配置、测试和 PPA 证据如何保持一致。使用 GPGPU-Sim 作为 execution-driven runtime、functional/timing simulator 分层、可配置 timing model、trace/statistics 和 power evidence plumbing 的参考。使用 Rocket Chip 作为 generator discipline 的参考：named configurations、negotiated bus/control protocols、tile/periphery boundaries、runtime-visible resources、protocol monitors 和 test harness integration。使用 XiangShan 作为复杂微结构文档参考：state ownership、generated parameters、core/tile/memory boundaries、LSQ replay、NEMU difftest 和 HPM/TopDown evidence。不要把 XiangShan 的 CPU OoO frontend、rename、ROB 或 precise-commit 语义复制成 SIMT 语义。

## 核心规则

在修改或提出任何 GPGPU 功能前，先给出层级影响表和分阶段验证路径。

| 层级 | 典型产物 | 必须回答的问题 |
|---|---|---|
| ISA | 指令语义、编码、CSR/DCR 状态 | 哪些架构状态会改变？ |
| 模拟器 | functional model、cycle model、golden trace | 可执行参考是什么？ |
| RTL | SIMT core、LSU、cache、CP、interconnect | valid-ready 和 stall 契约是什么？ |
| Runtime | device、buffer、queue、launch、event、fence | host 软件如何启动并观察工作？ |
| Kernel ABI | entry PC、args、grid/block/CTA/workgroup IDs | device 代码假设了什么？ |
| Config | 私有旋钮、ABI 常量、生成头文件 | 哪些值跨层可见？ |
| Tests | smoke、trace diff、regression、backend matrix | 什么能证明这一阶段可用？ |
| Evaluation | counters、logs、SAIF、synthesis reports | 哪个指标支撑这个变化？ |

不要静默修改多个层级。列出每个受影响层级、每个契约的 owner，以及证明它仍然工作的最小 gate。

把系统集成视为生成出来的契约，而不是事后手工连线。任何新架构功能都必须说明由哪个 configuration fragment 打开、由哪个 tile/core/periphery 或 runtime-visible block 拥有、由哪些 protocol fields 承载，以及由哪个 monitor、trace 或 test harness 观察。

## 术语契约

新的设计和文档使用统一术语；只有在引用具体参考实现时保留源码原名。

| 统一术语 | 源码别名 | 含义 |
|---|---|---|
| SIMT group | warp、wavefront、wave | 共享 PC、scheduler residency 和 active lane mask 的 threads 或 work-items |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | 一个 resident SIMT group 的身份 |
| active lane mask | active mask、thread mask、`tmask`、`EXEC` mask | SIMT group 的 per-lane participation mask |
| CTA/workgroup | CTA、block、workgroup | 包含一个或多个 SIMT groups 的 launch group |
| compute core/CU | core、CU、compute unit | 拥有 SIMT groups 和 execution resources 的硬件单元 |

保持 `simt_group_width`、`active_mask_width`、`physical_simd_width`、`resident_simt_groups` 和 `test_thread_count` 分开记录。

## 必要契约

每个架构设计都应包含：

- Objective：正在测试的一个能力或假设。
- Non-goals：明确不做的高级功能。
- State contract：PC、active lane mask、SIMT group state、registers、memory、CSR/DCR、launch state。
- Config contract：将每个参数分类为 hardware-private、simulator-private、HW/SW ABI、test-only 或 debug-only。
- Launch contract：program image、kernel entry、args、grid/block dimensions、start、done、result、synchronization path。
- Simulation contract：functional oracle、timing model、shared kernel descriptor、trace schema 和 backend mode selection。
- Integration contract：memory/control protocol schema、source 或 tag 生命周期、resource/capability 暴露，以及 optional-feature ownership。
- Test gate：simulator smoke、RTL trace diff、runtime launch test、counter check 或 PPA report。
- Prototype credibility target：instruction unit tests、external golden trace、RTL simulation、FPGA smoke、benchmark run、synthesis report 或 ASIC estimate。
- Implementation anchors：说明哪个模块或计划模块拥有该声明。

对于需要落成可信 prototype 的架构方案，还要记录：

| 项 | 必填内容 |
|---|---|
| ISA scope | 已支持、计划支持、明确不支持的指令或功能 |
| CU organization | resident SIMT-group slots、issue width、active-mask width、physical SIMD width、SGPR/VGPR/LDS resources |
| Implementation anchors | fetch、wavepool、decode、issue、scoreboard、exec state、FU、LSU、dispatcher 或 control-plane owner |
| Evidence path | unit test、external oracle trace、RTL tracemon diff、FPGA control path、PPA report |
| Credibility caveat | relaxed frequency、area、power、tooling、ISA、runtime、memory hierarchy 或 benchmark assumptions |

不要把 SIMT-group width、active-mask width、physical SIMD width、resident SIMT-group slots 和 test thread count 混成一个模糊的 "lane count"。

## 阶段顺序

1. 定义项目骨架、ISA sketch、SIMT state、configuration boundary 和最小 launch path。
2. 在复杂 RTL 之前建立 functional simulator 或 golden trace、kernel descriptor 和 launch shape。
3. 实现最小 SIMT core：SIMT group state、active lane mask、scheduler、register file、ALU、commit。
4. 分阶段加入 memory：blocking LSU、lane masks 和 byte enables、outstanding tags、response demux，然后再 coalescing/cache。
5. 用 runtime 或 launch contract 替代 testbench pokes：load program、load args、start、wait、copy result。
6. 在扩展规模前加入 protocol/resource checks：request schema、source IDs、lane masks、ordering、capability exposure，以及至少一个 monitor 或 trace assertion。
7. 在调优前加入 counters：cycles、instructions、SIMT-group stalls、scoreboard stalls、memory stalls、load/store counts。
8. 只有在基本循环可调试后，才加入 cache、VM、tensor、graphics、FPGA 或软件生态工作。
9. 只有 correctness gates 通过后才使用 PPA。

## GPGPU-Sim 架构视角

当以 GPGPU-Sim 为参考时，将方案映射到这条链路：

| 契约 | GPGPU-Sim anchor | 本地架构问题 |
|---|---|---|
| Runtime entry | `cudaConfigureCallInternal`、`cudaSetupArgumentInternal`、`cudaLaunchInternal` | 后端接收前，哪个对象捕获 launch config 和 args？ |
| Work queue | `stream_manager`、`stream_operation` | memcpy、kernel launch、event、wait 和 completion 如何排序？ |
| Kernel descriptor | `kernel_info_t` | entry、grid/block dimensions、stream ID、CTA progress 和资源需求存在哪里？ |
| Functional oracle | `cuda-sim` | 哪个可执行模型拥有 ISA 和 memory semantics？ |
| Timing model | `shader_core_ctx`、`scheduler_unit`、`warp_inst_t` | 哪些状态只是 timing，哪些状态是 architectural？ |
| Memory hierarchy | `ldst_unit`、`mem_fetch`、L1/L2/DRAM/ICNT | 哪个 request carrier 在 memory 层级中保留 SIMT context？ |
| Config/evidence | `option_parser`、`gpgpusim.config`、stats、trace、AccelWattch | 哪个 workload、config、backend、counters 和 power assumptions 支撑结论？ |

把 GPGPU-Sim 当作可执行架构参考。把它的 C++ timing behavior 用作硬件指导前，先翻译成 RTL state、valid-ready、reset、flush、arbitration 和 backpressure。

## Rocket Chip Generator 视角

使用 Rocket Chip 作为把架构变成可复现 generated system 的参考：

| 契约 | Rocket Chip anchor | 本地架构问题 |
|---|---|---|
| named configuration | `Configs.scala`、`BaseConfig`、`DefaultConfig`、`With*` fragments | 哪个 config fragment 打开该功能，它影响哪些 generated values？ |
| tile boundary | `BaseTile.scala`、`RocketTile.scala` | 该功能属于 compute core、tile boundary、memory client、periphery，还是 runtime-visible resource？ |
| protocol negotiation | Diplomacy `LazyModule`、nodes、`Parameters.scala` | 哪些 width、ID range、address range 和 capability values 应该协商或检查，而不是硬编码？ |
| memory/control protocol | TileLink bundles、edges、monitors | 新路径有什么 request/response schema 和 executable protocol checks？ |
| accelerator control | `LazyRoCC.scala` | command、response、memory access、busy、interrupt、exception 和 optional ports 如何暴露？ |
| SoC resources | BootROM、debug、device resources、`ExampleRocketSystem`、`TestHarness` | 软件或 harness 如何发现、启动、调试和观察硬件？ |

不要把 Rocket 的 scalar CPU pipeline 复制成 SIMT 设计；借鉴的是它的 generator、boundary、protocol 和 verification discipline。

## XiangShan State-Owner 视角

使用 XiangShan 作为复杂微结构契约文档化的参考，重点是不要丢失 ownership boundary：

| 契约 | XiangShan anchor | 本地架构问题 |
|---|---|---|
| core/tile boundary | `XSCore.scala`、`XSTile.scala` | 哪个 block 拥有 SIMT state、memory clients、runtime-visible status、trace、debug 和 perf？ |
| derived microarchitecture | `Parameters.scala`、`BackendParams.scala`、`Configs.scala` | 哪些 width、queue、port 和 ID 是用户参数，哪些是派生检查？ |
| backend ownership | `Backend.scala`、`CtrlBlock.scala`、`TopDownGen.scala` | 哪个 unit 拥有 redirect、flush、recovery、issue、writeback、trace 和 bottleneck attribution？ |
| memory lifecycle | `MemBlock.scala`、`LSQWrapper.scala`、`LoadQueueReplay.scala` | memory request、replay、violation、wakeup 和 exception path 是什么？ |
| executable reference | `xiangshan-nemu/src/cpu/difftest/*` | final output 之前可以比较哪个中间状态或事件？ |
| performance evidence | PDF HPM 章节、`TopDownGen.scala`、`PMParameters.scala` | 每个 counter 由哪个 owner 发出，并如何汇总成 top-down explanation？ |

借鉴 state-owner、difftest 和 counter discipline。不要用 XiangShan 来证明 CPU-specific branch prediction、rename、ROB 或 hart/CSR 行为是 GPGPU 架构要求。

## Skill 路由

当任务主要集中在某个边界时，使用更窄的 skill：

| 任务形态 | 使用 |
|---|---|
| 参数或 ABI 变更 | `gpgpu-config` |
| 参考行为或 trace mismatch | `gpgpu-golden-sim` |
| SIMT RTL 状态或 pipeline | `gpgpu-rtl-simt-core` |
| LSU、cache、coalescing、memory ordering | `gpgpu-memory-path` |
| Host/device launch、queue、event、kernel entry | `gpgpu-runtime` |
| Performance、power、area、timing | `gpgpu-ppa-evaluation` |

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 RTL、simulator、runtime、ABI、config、tests 和 PPA 之间的 full-stack contract。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 MIAOW paper scope、CU source anchors、trace/test loop、FPGA control path，以及与架构工作相关的 prototype credibility caveats。

若想了解与本 skill 相关的 GPGPU-Sim 背景，请阅读本目录下的 `gpgpusim_local.md`。它说明 execution-driven runtime path、functional/timing split、shader/memory hierarchy、config、trace/statistics 和与架构决策相关的 power evidence。

若想了解与本 skill 相关的 Rocket Chip 背景，请阅读 `../../ref/skillref/rocket.md`，必要时再查看 `../../ref_submodule/rocket-chip`。重点关注 `Configs.scala`、Diplomacy docs、`BaseTile.scala`、`RocketTile.scala`、`LazyRoCC.scala`、TileLink monitor/fuzzer、`ExampleRocketSystem.scala` 和 `TestHarness.scala`。

若想了解与本 skill 相关的 XiangShan 背景，请阅读本目录下的 `xiangshan_local.md`。它说明 XiangShan 设计文档章节、`XSCore`/`XSTile` 边界、generated parameters、backend ownership、LSQ/replay、NEMU difftest 和与架构决策相关的 HPM/TopDown lessons。

## 常见错误

- 只画 RTL block diagram，却遗漏 runtime、config、tests 或 counters。
- 把 launch ABI 和 configuration 当成脚本细节，而不是架构契约。
- 在最小 SIMT loop 可 trace 之前加入 cache、VM、tensor、OpenCL、HIP、Vulkan 或 FPGA bring-up。
- 让 testbench-only internal pokes 变成永久 runtime interface。
- 一次改变多个变量，然后把结果称为架构结论。
- 把 C++ timing simulator path 当成可综合 RTL，却没有定义 hardware state、handshakes 和 reset/flush 行为。
- 硬编码本应生成、检查或作为 capability 暴露的 bus widths、source IDs、MMIO maps 或 optional feature ports。
- 复制 XiangShan 的 branch prediction、rename、ROB 或 precise commit 等 CPU 机制，却没有把它们翻译成 SIMT group、CTA/workgroup、active lane mask 和 kernel ABI 契约。
