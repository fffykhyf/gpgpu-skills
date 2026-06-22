---
name: gpgpu-ppa-evaluation
description: 用于评估 GPGPU performance、power、area、timing、energy、counters、bottlenecks、workload matrices、SAIF 或 VCD activity、synthesis reports、FPGA results、McPAT、GPUWattch、AccelWattch 或 architecture tradeoffs。
---

# GPGPU PPA Evidence Compiler Skill

## 1. Objective

把 verified traces、counters、reports 和 workload metadata 编译成受控的 performance/power/area claim，并向 architecture、config、RTL、memory 或 runtime 产生 causal feedback。

## 2. Input Contract

输入是 evaluation intent，必须包含 baseline candidate、variant candidate、workload、backend、config digest、correctness gate、metric target 和 expected feedback owner。

## 3. PPA State Model

| Evidence state | Required binding |
|---|---|
| launch state | kernel image、args、grid/block shape、queue timeline、launch latency |
| compute state | PC/mask/register effects、issued SIMT groups、occupancy、divergence |
| dependency state | scoreboard stalls、operand stalls、replay、barrier、hazard graph counters |
| memory state | load/store count、coalescing、cache hits/misses、MSHR、bank、NoC/L2/DRAM pressure |
| pipeline state | fetch/decode/issue/execute/writeback utilization and stalls |
| config state | source config、derived topology、ABI version、backend、commit/report path |
| physical state | area hierarchy、timing/Fmax/WNS、power/energy、activity source |

## 4. 固定五问

每个 PPA claim 必须回答：

1. What state exists? 指明 workload、config、launch、compute、memory、dependency、pipeline 或 physical state。
2. Who produces it? Trace、counter owner、synthesis tool、power model、runtime 或 benchmark harness。
3. Who consumes it? Architecture decision、config update、RTL/memory/runtime feedback 或 report。
4. How does it change? 定义 baseline-to-variant controlled diff 和 causal path。
5. How do we verify it? 指明 correctness gate、counter audit、report provenance、reproducibility command。

## 5. Baseline Definition

Baseline 必须严格包含：

- exact commit 和 config digest。
- backend：golden sim、RTL sim、FPGA、synthesis、analytic model 或 power model。
- workload 和 input size。
- launch shape 和 runtime path。
- correctness status 和 trace/regression gate。
- metric collection commands 和 report paths。
- known limitations 和 unsupported features。

没有 baseline 就没有 improvement claim。

## 6. Variant Definition

Variant 必须是 controlled diff：

- 只改变一个 intended architecture/config/RTL/memory/runtime variable。
- 所有无关 config、workload、tool、backend inputs 保持不变。
- 记录 generated topology summary。
- 保留 monitor/assertion status。
- 多变量改变时标记为 exploratory，并拆分 follow-up experiments。

## 7. Workload Model

Workload record 必须包含 kernel/benchmark name/version、input data、memory image、random seeds、launch dimensions、local/shared memory、runtime queue/event/fence path、warmup/sampling/checkpoint/region selection、correctness oracle 和 expected output/trace status。

## 8. Metric Model

| Metric class | Required fields |
|---|---|
| latency | total cycles/time、launch latency、kernel cycles、memory latency、queue wait |
| throughput | IPC、issued SIMT groups、active lanes、occupancy、memory bandwidth |
| energy | power model、activity source、duration、dynamic/static split、calibration caveat |
| area | hierarchy、technology/device、resource type、generated features、utilization |
| timing | target clock、achieved Fmax、WNS/TNS、critical path owner、constraints |

Counters 必须命名 producer modules、trigger conditions 和 reset/sample windows。

## 9. Transformation Rules: Causal Attribution Engine

| Bucket | Evidence required |
|---|---|
| scheduler gain | 更少 scheduler idle cycles、更高 ready SIMT groups、更低 scoreboard stalls |
| memory gain | 更低 memory latency、更少 misses/replays/bank conflicts/MSHR stalls、更高 coalescing efficiency |
| compute gain | 更高 FU utilization、更低 execute latency、更少 issue/operand stalls |
| launch/runtime gain | 更低 queue wait、launch latency、transfer/fence overhead |
| config effect | topology/resource change 绑定 generated config 和 capability output |
| artifact/noise | tool variance、workload sampling、frequency change、incorrect baseline、missing correctness gate |

不能从单个 summary speedup number 声称原因。

## 10. State Evolution

PPA state 从 verified baseline/variant records 演化成 causal evidence graph。每个 metric change 都必须追溯到 changed GPU state，并作为 feedback 路由给能行动的 contract owner。

## 11. Evidence Graph

每份 report 都应构建：

```text
controlled diff
  -> changed GPU state
  -> changed counter/trace event
  -> changed metric
  -> supported claim
  -> feedback target
```

Feedback target 可以是 architecture、config、runtime、golden sim、RTL 或 memory。

## 12. Output Contract

PPA output 必须包含 baseline record、variant record、workload model、metric table、correctness gate status、counter/trace provenance、area/timing/power provenance、causal attribution graph、limitations 和 next feedback target。

## 13. Verification Gate

| Gate | Required proof |
|---|---|
| correctness | baseline 和 variant 通过 smoke/regression/oracle trace gate |
| reproducibility | commands、config digests、report paths、workload inputs recorded |
| controlled diff | 只改变一个 intended variable，或标记 exploratory |
| counter audit | counters 映射到 owner modules，并解释 metric direction |
| physical audit | tool/device/technology/clock/activity source recorded |
| attribution | evidence graph 连接 state change 到 metric change |
| feedback | 指明下一步 architecture/config/RTL/memory/runtime action |

## 14. Design Evidence Layer

| Evidence | Use |
|---|---|
| GPGPU-Sim/AccelWattch | simulator counters、traces、activity、model caveats 的 behavioral/power-model evidence |
| Rocket Chip | local perf events、generated configs、harness/regression evidence 的 structural reference |
| Vortex/MIAOW | GPU synthesis、FPGA、benchmark、prototype credibility 的 implementation anchors |
| XiangShan | HPM ownership、top-down bottleneck、checkpoint methodology 的 tradeoff justification |
| papers | 只有 baseline、variant、workload、limitations 可比时才作为 empirical justification |

Framework 和 paper 只能支持 evidence nodes，不能替代 causal analysis 成为 report sections。

## 15. Failure Modes

- speedup 没有 baseline、variant、workload、config、correctness gate。
- 多变量改变却写成 causal conclusion。
- simulator counters 被当成 silicon timing 或 power。
- SAIF/VCD、power model、synthesis report 脱离 workload/config。
- counter 有名字但 producer module 和 trigger condition 不清楚。
- PPA feedback 没有路由到具体 contract owner。
