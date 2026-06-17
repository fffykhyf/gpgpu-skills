# GPGPU RTL SIMT Core

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

这个 skill 用于 GPGPU 的最小计算核心。它要求 SIMT 架构状态保持显式，并把 RTL 模块边界控制在可测试、可 trace 的范围内。

## 核心规则

每次 RTL 修改前，先定义状态契约：

- 每个 warp 的 PC。
- active mask 和 predicate 行为。
- warp 状态：idle、ready、running、stalled、done、waiting at barrier 或 replaying。
- register file 读规则和 writeback 规则。
- scoreboard 或 hazard 规则。
- pipeline valid-ready、stall、flush、reset 和 kill 行为。

如果这些内容无法清楚表述，说明模块边界可能过大。

## 推荐模块边界

| 模块区域 | 职责 |
|---|---|
| Warp scheduler | 选择 ready warp 并暴露 stall reason |
| Fetch/decode | 把 PC 和 instruction bits 转换成 control fields |
| Scoreboard | 跟踪 register 和 memory hazard |
| Operand collector | 收集 source operands，但不隐藏 hazard |
| Register file | 持有架构 register，并定义 writeback conflict 规则 |
| Functional units | 执行 ALU、branch、SFU 或其他操作 |
| Commit/writeback | 应用架构效果并输出 trace event |

避免一个模块同时 decode、schedule、read register、execute、writeback 并控制 memory。

## 实现检查清单

修改 RTL 前：

- 找到对应 simulator 行为或 golden trace。
- 说明这个修改是架构行为、纯时序行为，还是仅测试行为。
- 定义受影响信号及其有效周期。
- 说明每个接口的 backpressure 行为。
- 增加或更新能到达该路径的 smoke test。

修改 RTL 后：

- 比较 simulator 和 RTL 的架构效果。
- 检查 reset 行为以及 empty/invalid input 行为。
- 如果接口可能 stall，至少检查一个 stall 或 backpressure case。
- 保持 PC、warp、active mask、writeback 和 memory event 的 trace 可见性。

## 常见错误

- 把 active mask 当作临时实现细节，而不是 SIMT 核心状态。
- 加入 branch 或 barrier 行为时，没有说明 reconvergence 或 wakeup 规则。
- 把 hazard 行为隐藏在 operand read 逻辑里。
- 让 stall handling 依赖无关 always block 之间的隐式顺序。
- 只靠 waveform 浏览调试 RTL，而不做 trace alignment。
