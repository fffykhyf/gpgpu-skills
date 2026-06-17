# GPGPU PPA Evaluation

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

当 GPGPU 修改需要功能正确性之外的证据时，使用这个 skill。PPA 工作必须把 performance、power、area 和 timing 结论绑定到 counter、report 和受控对比。

## 核心规则

没有 baseline、workload、configuration、metric 和可复现 command/report path，就不要宣称优化更好。

## 最小评估记录

每个结果都要记录：

| 项目 | 必需内容 |
|---|---|
| Baseline | 修改前的 commit/config/parameter set |
| Variant | 修改后的 commit/config/parameter set |
| Workload | program、input size、launch config、memory image |
| Backend | simulator、RTL sim、FPGA、synthesis 或 analytic model |
| Metrics | cycles、IPC、stalls、bandwidth、power、area、timing 或 energy |
| Evidence | log path、trace path、report path 或 command |
| Interpretation | 发生了什么变化，以及仍不确定的部分 |

## Counter 优先

在做性能判断前，优先加入 counter：

- total cycles
- committed instructions
- IPC
- issued warps
- scoreboard stalls
- memory stalls
- barrier stalls
- load/store request count
- coalesced request count
- cache 存在时的 hits/misses

如果缺少 counter，必须说明当前结论是假设还是测量事实。

## PPA 工作流

1. 定义假设和瓶颈。
2. 选择能触发瓶颈的最小 benchmark。
3. 运行 baseline 并保存日志。
4. 在相同配置下运行 variant。
5. 先比较 counter，再看总 speedup。
6. 对 power 或 area，把 simulator/RTL activity 映射到 McPAT、GPUWattch、AccelWattch 或 synthesis report。
7. 报告退化和测量限制。

## 常见错误

- 报告 speedup 但不展示 cycle 和 stall breakdown。
- 比较不同 config 或 workload，却声称是架构收益。
- 不加说明地把 simulator counter 当作硅上 timing 或 power。
- 只优化 IPC，却忽略 bandwidth、energy 或 area。
- 只保留 summary number，丢失复现所需 report path。
