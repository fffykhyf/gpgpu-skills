# GPGPU Golden Simulator

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

当 simulator 行为、指令语义或 trace 对比是事实来源时，使用这个 skill。Simulator 应该是架构的可执行镜像和 RTL 调试 oracle，而不是只检查最终输出。

## 核心规则

每个非平凡 RTL 行为，在被信任前都应该有 simulator 行为或 golden trace。调 bug 时，先找到 reference 和实现之间的第一处分歧，再提出硬件修复。

## Module Twin Map

每个新增 RTL block 都要说明 simulator 中由谁镜像：

| 硬件概念 | simulator 中的所有者 |
|---|---|
| warp scheduler、PC、mask、barrier | scheduler 或 warp state model |
| decode 和 instruction expansion | decoder 和 sequencer |
| scoreboard 和 hazard | scoreboard model |
| register read/writeback | operand 或 register-file model |
| ALU/FPU/SFU/LSU/TCU | functional unit model |
| memory hierarchy | LSU、coalescer、cache、memory model |
| launch 和 CTA dispatch | runtime/KMU/CTA model |

避免用一个中心解释器绕过时序和模块边界。ISA 语义应靠近拥有该行为的执行单元。

## Trace 契约

一条有用的 trace 记录应包含：

| 类别 | 字段 |
|---|---|
| identity | cycle 或 step、sequence ID 或 UUID、core ID、warp ID |
| control | PC、next PC、opcode、active mask、predicate mask |
| operands | source registers、source values、destination register |
| commit | writeback valid、value、exception 或 illegal instruction |
| memory | op、lane mask、address、byte enable、data、tag、response |
| scheduling | scoreboard block、operand block、memory block、barrier block、replay |

如果省略字段，必须说明当前阶段为什么不需要。

## First-Divergence 工作流

1. 实现前定义指令语义：输入、输出、状态变化、非法情况和 mask 行为。
2. 在复杂 RTL 前先加入或更新 simulator 行为。
3. 输出能触发该行为的最小 golden trace。
4. 用相同 program、config、input memory 和 launch shape 运行 RTL 或第二个 backend。
5. 先 diff 有序架构效果，再 diff 时序字段。
6. 报告第一处分歧，并给出足够复现上下文。
7. 判断违反契约的是 simulator、RTL、memory path、runtime 还是 test harness。

不要为了匹配 RTL 输出就直接修改 simulator。先判断哪一侧违反架构契约。

## 常见错误

- 只比较最终 memory output，而第一处错误 writeback 早已发生。
- 等 bug 出现后才补 trace 字段，而不是早期定义最小 trace 契约。
- 把功能正确性和时序精度混进一个含义不清的 trace。
- 让 simulator 结构和 RTL 完全脱节，导致 trace diff 难以映射回模块。
- 没有重跑复现输入和至少一个回归测试，就宣称修复完成。

如果需要了解更多和本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.zh.md`。它已经整理了相关 Vortex 设计文档和代码路径的要点，日常 simulator 与 trace 工作不需要重新通读整个 reference tree。
