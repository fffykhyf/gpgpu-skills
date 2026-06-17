# GPGPU PPA Evaluation

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

当 GPGPU 修改需要功能正确性之外的证据时，使用这个 skill。PPA 结论必须把 workload、backend、configuration、counter、activity 和 report 绑定成受控对比。

## 核心规则

没有 baseline、variant、workload、configuration、backend、metric、evidence path 和 interpretation，就不要宣称设计更好。

## 最小评估记录

| 字段 | 必需内容 |
|---|---|
| config_id | commit、build flags、core/warp/thread、memory/cache、ISA/features |
| baseline | 未修改参考设计及精确 command 或 report path |
| variant | 只改变一个目标变量后的设计 |
| workload | kernel 或 benchmark、input size、launch shape、memory image |
| backend | simulator、RTL sim、synthesis、FPGA 或 analytic model |
| correctness | pass/fail、trace diff 状态、已知限制 |
| counters | cycles、instrs、IPC、stalls、load/store、cache、memory |
| reports | area、timing、Fmax、power、SAIF/VCD 或模型输出 |
| interpretation | 数据支持什么，不支持什么 |

如果多个变量同时变化，拆分实验；否则标记为 exploratory。

## Correctness Before PPA

按这个顺序：

1. Correctness gate：smoke/regression/trace diff 通过。
2. Performance gate：counter 能解释观察到的 speedup 或 slowdown。
3. Area/timing gate：synthesis 或 FPGA report 显示资源和频率影响。
4. Power/energy gate：说明是 vectorless 还是 activity-annotated 估计。

错误设计的 IPC 不是有用证据。

## Counter Schema

调优前优先加入 counter：

- total cycles 和 committed instructions
- IPC 和 issued warps
- scheduler idle 和 active warps
- scoreboard、operand、ALU/FPU/LSU/SFU/TCU stalls
- branch 和 divergence counts
- load/store requests 和 latency
- coalescer misses 或 merge rate
- cache reads/writes、misses、bank stalls、MSHR stalls

如果缺少 counter，必须说明当前结论是假设还是测量事实。

## Power And Area 纪律

- 报告 target clock、tool、device 或 technology、build flags。
- 区分 vectorless power 和 SAIF/VCD-annotated power。
- SAIF/VCD 必须绑定生成它的 workload。
- 记录 WNS 和 estimated Fmax，不只写 timing passed。
- 如果改动局部化，保留 hierarchical area 和 power。

## 常见错误

- 报告 speedup 但不展示 cycle 和 stall breakdown。
- 比较不同 config 或 workload，却声称是架构收益。
- 不加 caveat 地把 simulator counter 当作硅上 timing 或 power。
- 使用来自不同 workload 或 config 的 SAIF/VCD。
- 只保留 summary number，丢失 command 或 report path。

如果需要了解更多和本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.zh.md`。它已经整理了相关 Vortex 设计文档和代码路径的要点，日常 PPA 工作不需要重新通读整个 reference tree。
