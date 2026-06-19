---
name: gpgpu-ppa-evaluation
description: 用于评估 GPGPU performance、power、area、timing、energy、counters、bottlenecks、workload matrices、SAIF 或 VCD activity、synthesis reports、FPGA results、McPAT、GPUWattch、AccelWattch 或 architecture tradeoffs。
---

# GPGPU PPA Evaluation

## 概览

当 GPGPU 变更需要 functional correctness 之外的证据时使用本 skill。PPA 结论必须把 workload、backend、configuration、counters、activity 和 reports 绑定到受控对比中。使用 Rocket Chip 作为把 named configs、local perf events、cache/memory counters、traces、regression flows 和 generated hardware evidence 串起来的参考。使用 XiangShan 作为 HPM event ownership、TopDown bottleneck decomposition、checkpoint/SimPoint methodology，以及区分 research prototype evidence 和 architecture claims 的参考。

## 核心规则

没有 baseline、variant、workload、configuration、backend、metric、evidence path 和 interpretation，就不要声称设计更好。报告前先分类结果：

| 声明 | 必要证据 |
|---|---|
| optimization claim | controlled baseline 和 variant，且只改变一个预期变量 |
| credibility claim | working correctness path 加 RTL、FPGA、synthesis、benchmark 或 power/area evidence，证明 prototype 真实存在 |
| exploratory observation | 多个变量变化或 counters 不完整；标注为 hypothesis |

Credibility claim 可以引用 ISA scope、benchmark capability、FPGA prototype data 和 ASIC-style estimates，但同时必须说明 relaxed design goals 和 comparison caveats。

任何 PPA 声明还必须识别 generated configuration 和 instrumentation contract。如果变更影响 protocol widths、source IDs、cache/MSHR resources、optional units、runtime queues 或 memory maps，报告必须说明哪些 counters 或 traces 证明被评估的 configured hardware 正是该硬件。

## 术语契约

Config IDs、counter names 和 PPA tables 使用统一术语；只有报告具体 backend counter 时保留源码别名。

| 统一术语 | 源码别名 | Evaluation 含义 |
|---|---|---|
| SIMT group | warp、wavefront、wave | 用于 issue、stalls、occupancy 和 launch shape 计数的 scheduling group |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | 报告 per-group 数据时的 trace/counter identity |
| active lane mask | active mask、thread mask、`tmask`、`EXEC` mask | lane utilization 和 divergence evidence |
| CTA/workgroup | CTA、block、workgroup | workload launch unit 和 local-memory/barrier scope |
| compute core/CU | core、CU、compute unit | area、power、counters 和 occupancy 的 resource unit |

## 最小 Evaluation Record

| 字段 | 必填内容 |
|---|---|
| config_id | commit、build flags、compute core/CU、SIMT-group/thread、memory/cache、ISA/features |
| baseline | 未改变参考，带 exact command 或 report path |
| variant | 变更设计，且只改变一个预期变量 |
| workload | kernel 或 benchmark、input size、launch shape、memory image |
| backend | simulator、RTL sim、synthesis、FPGA 或 analytic model |
| correctness | pass/fail、trace diff state、known limitations |
| counters | cycles、instrs、IPC、stalls、load/store、cache、memory |
| reports | area、timing、Fmax、power、SAIF/VCD、trace、visualization 或 model output |
| interpretation | 数据支持什么、不支持什么 |

如果改变了多个变量，拆分实验，或把结果标为 exploratory。

对于 generated designs，记录 config fragment 或 option dump、derived topology summary、存在时的 public capability/version output，以及被测 protocol 的 monitor status。

## Correctness Before PPA

使用以下顺序：

1. Correctness gate：smoke/regression/trace diff 通过。
2. Performance gate：counters 能解释观察到的 speedup 或 slowdown。
3. Area/timing gate：synthesis 或 FPGA reports 展示 resource 和 frequency impact。
4. Power/energy gate：说明 vectorless 或 activity-annotated estimate。

错误设计的 IPC 不是有用证据。

## Counter Schema

调优前优先添加 counters：

- total cycles 和 committed instructions
- IPC 和 issued SIMT groups
- scheduler idle 和 active SIMT groups
- scoreboard、operand、ALU/FPU/LSU/SFU/TCU stalls
- branch 和 divergence counts
- load/store requests 和 latency
- coalescer misses 或 merge rate
- cache reads/writes、misses、bank stalls、MSHR stalls
- 建模后还要包含 replay、nack、kill、flush、TLB miss、uncached/MMIO、source/tag exhaustion 和 ordering/fence stalls
- 建模后还要包含 runtime launch latency、command queue occupancy、completion latency、memory latency、interconnect/L2/DRAM queue pressure 和 trace sampling scope

如果缺少 counters，说明结论是 hypothesis 还是 measured fact。

## XiangShan HPM 和 TopDown 模式

使用 XiangShan 作为解释结果为什么变化的证据参考：

| 证据契约 | XiangShan anchor | 本地 PPA 规则 |
|---|---|---|
| hardware event ownership | PDF HPM 章节、`PMParameters.scala` | 将 counters 放在拥有事件的模块附近，并文档化 trigger conditions。 |
| counter selection | `mhpmcounter3-31`、HPM event selectors | 保持 event selection、grouping、privilege/sample domain 和 overflow behavior 可复现。 |
| top-down attribution | `TopDownGen.scala`、debugTopDown ports | 先把 counters 汇总为 bottleneck classes，再声称具体 optimization cause。 |
| memory bottlenecks | LSU/DCache/MMU/CoupledL2 章节 | 区分 replay、TLB miss、DCache miss、MSHR full、uncache/MMIO、L2 和 protocol stalls。 |
| workload sampling | NEMU checkpoint 和 SimPoint flow | 对长 workload 使用 checkpoints、sampled regions 和 weights，而不是 ad hoc partial runs。 |
| artifact discipline | XiangShan MICRO methodology | 将 functional verification、debug traces、performance validation 和 artifact provenance 绑定在一起。 |

本地 GPGPU 工作中，把 frontend/backend/memory/cache 翻译成 launch/dispatch、scheduler/issue、SIMT divergence、register/operand、LSU/coalescer、cache/TLB/NoC/DRAM、barrier 和 atomic classes。

## Rocket Chip Evidence 模式

使用 Rocket Chip 作为将证据放在逻辑附近的参考：

| 证据 | Rocket Chip anchor | 本地规则 |
|---|---|---|
| core events | `RocketCore` event sets | 在 owner module 处统计 issue、stalls、replay、flush、branch/divergence 和 unit interlocks。 |
| cache/memory events | `HellaCachePerfEvents`、DCache events | 在 memory path 中统计 misses、grants/responses、blocked cycles、TLB misses、uncached/MMIO 和 queue pressure。 |
| trace path | `trace/` encoder/controller/sink | 把 trace configuration、sampling scope 和 event schema 与报告一起保留。 |
| config comparison | named `Configs.scala` fragments | 对比只改变一个预期变量的 named configs。 |
| harness/regression | `TestHarness`、`regression/`、Verilator support | 解释 counters 前先记录 correctness gate 和 backend。 |

借鉴 evidence discipline，而不是 Rocket 的 CPU-specific event meanings。

## GPGPU-Sim Evidence Loop

使用 GPGPU-Sim 作为 simulator-based evidence 的参考：

1. 记录 workload、input size、kernel name、launch shape 和 runtime path。
2. 记录 config file path 或 digest。
3. 在读取 performance 前先跑 correctness gate。
4. 收集 core counters：cycles、instructions、issue rate、active/idle SIMT groups、scheduler stalls。
5. 收集 memory counters：load/store count、memory latency、cache hits/misses、MSHR stalls、ICNT/L2/DRAM pressure。
6. 只有在记录 component/core/memory-partition sampling 后才使用 trace samples。
7. 如果使用 AccelWattch 或其他 power model，记录 model version、XML/config file、activity source 和 calibration caveat。
8. 与只改变一个预期变量的 baseline 对比。

Simulator counters 可以支撑 architecture hypotheses 和 bottleneck analysis。它们本身不是 RTL timing closure 或 silicon power evidence。

## Power 和 Area 纪律

- 报告 target clock、tool、device 或 technology、build flags。
- 区分 vectorless power 和 SAIF/VCD-annotated power。
- 将 SAIF/VCD 绑定到产生它的 workload。
- 记录 WNS 和 estimated Fmax，而不仅是 "timing passed"。
- 当变化局部化时，保留 hierarchical area 和 power。
- 与 commercial GPU 或 paper number 对比时，说明 process node、clock、CU count、memory system、compiler/runtime path、workload、estimation method，以及哪些目标被 relaxed。不要用 research prototype credibility number 暗示设计已经 PPA-optimal。

## 常见错误

- 报告 speedup，却没有 cycle 和 stall breakdown。
- 比较不同 configs 或 workloads，却称为 architecture win。
- 把 simulator counters 当成 silicon timing 或 power，且没有 caveats。
- 使用来自不同 workload 或 config 的 SAIF/VCD。
- 报告 AccelWattch、McPAT 或 GPUWattch output，却没有 model version、config、activity source 和 calibration status。
- 只保留 summary numbers，却丢失 command 或 report path。
- 在离事件 owner 很远的地方添加 counters，导致无法和 trace 或 RTL behavior 对齐。
- 对比 generated variants，却没有记录 config fragment、derived topology 和 protocol monitor status。
- 声称 XiangShan-style top-down bottleneck，却没有展示其背后的 counter owner、workload sample、config 和 correctness gate。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 synthesis reports、counters、backend evidence 和 PPA 工作的 full-stack reproducibility。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 MIAOW paper 中的 FPGA、area、power、performance、OpenCL/Rodinia 和 comparison evidence，以及防止 overclaiming 的 caveats。

若想了解与本 skill 相关的 GPGPU-Sim 背景，请阅读本目录下的 `gpgpusim_local.md`。它说明 reproducible config records、runtime/cycle/memory counters、trace sampling、AerialVision、AccelWattch 和 power-model caveats。

若想了解与本 skill 相关的 Rocket Chip 背景，请阅读 `../../ref/skillref/rocket.md`，必要时查看 `../../ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala`、`rocket/HellaCache.scala`、`trace/`、`system/TestHarness.scala`、`regression/` 和 `src/main/resources/csrc/`。

若想了解与本 skill 相关的 XiangShan 背景，请阅读本目录下的 `xiangshan_local.md`。它说明 HPM/TopDown counters、backend 和 memory event ownership、NEMU instruction/profiling support、checkpoint/SimPoint flow，以及如何把这些证据模式适配到 GPGPU PPA evaluation。
