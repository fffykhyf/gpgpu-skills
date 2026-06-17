# GPGPU RTL SIMT Core

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

这个 skill 用于 GPGPU 的最小计算核心。SIMT 状态必须显式，模块边界必须足够小，并且 RTL 行为要能和 simulator trace 对齐。

## 核心规则

每次 RTL 修改前，先定义状态契约：

- 每个 warp 的 PC。
- active mask 和 predicate 行为。
- warp 生命周期：inactive、ready、issued、waiting、barrier、replay、done。
- 控制流变化时的 IPDOM、split、join、branch 和 reconvergence 状态。
- register file 读写规则和写冲突规则。
- scoreboard 的 set、clear、flush、reset 和 kill 规则。
- pipeline valid-ready、stall、flush、reset 和 kill 行为。

如果这些内容无法清楚表述，说明模块边界太大，或者架构契约不完整。

## 推荐流水线边界

| 阶段或单元 | 职责 |
|---|---|
| schedule | 选择 ready warp，暴露 stall reason，跟踪生命周期 |
| fetch | 按 PC 请求指令并处理 I-cache response |
| decode | 把 instruction bits 转成 control fields |
| issue | 缓存 decoded instruction，检查 hazard，选择 issue slot |
| operands | 读 register，但不隐藏 hazard 所有权 |
| dispatcher | 把 issue slot 路由到 ALU/FPU/LSU/SFU/TCU |
| execute | 产生执行结果和 memory request |
| commit | 应用 writeback，更新 scoreboard，输出 trace |

避免一个模块同时 schedule、decode、read register、execute、writeback 并驱动 memory。

## 指令影响检查

每条 instruction 或 uop class 都要说明是否改变：

- PC 或 next PC。
- active mask、predicate mask、split/join stack 或 warp status。
- integer、floating、vector 或 predicate registers。
- scoreboard 或 in-flight state。
- memory request、response、fence 或 replay state。
- barrier、CTA、CSR 或 launch-visible state。

## Bring-up 顺序

1. 单 warp、单 issue、ALU-only、无 divergence。
2. 多 warp round-robin scheduler。
3. register writeback 和 scoreboard。
4. active mask 和 predicated execution。
5. branch 加简化 divergence/reconvergence 状态。
6. 通过 memory-path 契约接入 LSU。
7. barrier、CTA dispatch 和完整 warp 生命周期。

## 常见错误

- 把 active mask 当作临时信号，而不是 SIMT 核心状态。
- 加入 branch 或 barrier 行为时，没有 reconvergence 或 wakeup 规则。
- 把 hazard 行为隐藏在 operand read 逻辑里。
- 让 backpressure 依赖无关 always block 之间的隐式顺序。
- 只靠 waveform 浏览调试，而不做 simulator/RTL trace alignment。

如果需要了解更多和本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.zh.md`。它已经整理了相关 Vortex 设计文档和代码路径的要点，日常 SIMT RTL 工作不需要重新通读整个 reference tree。
