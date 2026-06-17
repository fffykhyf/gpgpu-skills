# GPGPU Config

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

当某个值可能在 RTL、simulator、runtime、kernel、tests 或 PPA scripts 之间漂移时，使用这个 skill。配置工作不是简单把数字换成宏，而是判断哪些值是私有实现参数，哪些值是可见契约。

## 核心规则

修改任何参数前，先归类：

| 类别 | 含义 | 典型例子 |
|---|---|---|
| hardware-private | 只影响 RTL 和综合微架构 | queue depth、cache MSHR size、pipeline latency |
| simulator-private | 只影响模型 debug 或时序 | simulator verbosity、synthetic latency |
| HW/SW ABI | RTL 和软件都可见 | CSR/DCR map、memory map、kernel args、capability bits |
| test-only | 只限测试或 fixture | small smoke-test memory size |
| debug-only | instrumentation、trace、assertions | trace level、watchdog timeout |

HW/SW ABI 值必须有单一事实来源，并通过 RTL、simulator、runtime、kernel 和 tests 的验证路径。

## 修改检查清单

每次 config 修改都要：

- 说明参数类别。
- 找到单一事实来源。
- 列出生成或同步的消费者。
- 说明 public capability、version 或 query output 是否变化。
- 删除重复 hard-coded copy。
- 至少测试一个小配置和一个目标配置。
- 如果影响评估，更新 PPA config ID。

## 边界规则

- hardware-private knob 可以调实现，但不能泄漏到 public runtime header。
- ABI constant 必须通过生成头、文档 map 或显式 capability query 被所有消费者看到。
- debug/test knob 不能变成永久架构假设。
- derived value 应由 source value 生成，不要手工复制。
- 修改 visible config 却不更新测试和 capability reporting 是 bug。

## Drift 信号

看到这些情况时立即使用本 skill：

- lane、warp、core、register、cache 或 memory size 被复制在多个文件。
- simulator 和 RTL 使用不同 constant。
- runtime 从 build flags 猜硬件 capability。
- 测试只在某个 hard-coded configuration 下通过。
- PPA 结果无法重建 config。

## 常见错误

- 把所有数字都当成同一种宏。
- 混用 microarchitecture knob 和 software ABI constant。
- 更新 RTL 后，让 simulator、runtime 或 tests 留着旧值。
- 修改 memory map 或 CSR/DCR 编号，却没有 capability 或 version 方案。
- 修改参数化逻辑后只跑 default config。

如果需要了解更多和本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.zh.md`。它已经整理了相关 Vortex 设计文档和代码路径的要点，日常 config 与 ABI 工作不需要重新通读整个 reference tree。
