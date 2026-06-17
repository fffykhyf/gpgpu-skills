# GPGPU Golden Simulator

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

当 simulator 行为、指令语义或 trace 对比是 GPGPU 开发的事实来源时，使用这个 skill。Simulator 的作用不是只预测最终输出，而是让 RTL bug 可以被定位到具体行为。

## 核心规则

每个非平凡 RTL 行为，在被信任前都应该有 simulator 或 golden trace 作为参考。调 bug 时，先定位第一处行为分歧，再提出硬件修复。

## Trace 契约

一条有用的 trace 记录应包含跨 backend 对比所需字段：

| 字段 | 目的 |
|---|---|
| cycle 或 step | 排序事件并识别第一处分歧 |
| core、warp、lane mask | 标识正在执行的 SIMT 上下文 |
| PC 和 instruction | 把行为绑定到 ISA 语义 |
| active mask 或 predicate | 解释 SIMT lane 参与情况 |
| source operands | 在可行时解释执行输入 |
| register writeback | 比较架构效果 |
| memory request | 比较 address、byte enable、tag 和 data |
| stall 或 replay reason | 解释可见时序行为 |

如果省略某个字段，说明为什么当前阶段不需要它。

## 工作流

1. 在实现前定义指令语义：输入、输出、状态变化、非法情况和 mask 行为。
2. 对新 ISA 或执行行为，先加入或更新 simulator 行为。
3. 为能触发该行为的最小程序输出 golden trace。
4. 用同一个程序运行 RTL 或第二个 backend。
5. 先比较有序架构效果，再比较时序字段。
6. 报告第一处分歧，并给出足够复现上下文。

## 调试纪律

遇到 mismatch 时记录：

- 复现输入：program、config、input memory 和 command。
- 期望事件：simulator trace 行或 golden state。
- 实际事件：RTL trace 行或观测状态。
- 第一处分歧：不是最终错误输出。
- 怀疑层次：ISA、simulator、RTL、memory path、runtime 或 test harness。
- 下一步验证：能证明修复的最小 trace 或 test。

## 常见错误

- 只比较最终 memory output，而第一处错误 writeback 早已发生。
- 把功能正确性和时序精度混进一个含义不清的 trace。
- 让 simulator 结构和 RTL 结构完全脱节，导致 diff 结果难以映射回模块。
- 等到 bug 出现后才补 trace 字段，而不是早期定义最小 trace 契约。
- 没有重跑复现输入和至少一个回归测试，就宣称 RTL bug 已修复。
