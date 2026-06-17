---
name: gpgpu-rtl-simt-core
description: 用于设计、编辑或评审 GPGPU SIMT RTL，包括 warp lifecycle、PC、active masks、IPDOM、split/join、fetch/decode、scheduler、scoreboard、operands、register file、functional units、valid-ready、stall、flush 或 commit 行为。
---

# GPGPU RTL SIMT Core

## 概览

用于 GPGPU 的最小 compute core 工作。保持 SIMT state 明确、模块边界小，并让 RTL 行为能够和 simulator trace 对齐。

## 核心规则

每个 RTL 变更在编辑逻辑前，都必须先定义 state contract：

- 每个 warp 的 PC。
- Active mask 和 predicate 行为。
- Warp lifecycle：inactive、ready、issued、waiting、barrier、replay、done。
- 如果控制流变化，说明 IPDOM、split、join、branch 和 reconvergence state。
- Register file read/writeback 和 write conflict 规则。
- Scoreboard set、clear、flush、reset 和 kill 规则。
- Pipeline valid-ready、stall、flush、reset 和 kill 行为。

如果这些规则无法清楚说明，说明模块边界太宽，或架构契约不完整。

## 推荐 Pipeline 边界

| Stage 或 unit | 职责 |
|---|---|
| schedule | 选择 ready warp，暴露 stall reason，跟踪 lifecycle |
| fetch | 按 PC 请求指令并处理 I-cache response |
| decode | 将 instruction bits 转成 control fields |
| issue | 缓冲 decoded instructions、检查 hazards、选择 issue slots |
| operands | 读取寄存器，但不隐藏 hazard owner |
| dispatcher | 将 issue slots 路由到 ALU/FPU/LSU/SFU/TCU |
| execute | 产生 unit results 和 memory requests |
| commit | 应用 writeback、更新 scoreboard、发出 trace |

避免用一个模块同时完成 schedule、decode、read registers、execute、write back 和 drive memory。

在实现 issue 或 hazard 逻辑前，state contract 还必须列出拥有 readiness 的 per-wavefront tables：

| 表 | 职责 |
|---|---|
| valid entry | decoded instruction residency，以及在 halt、branch、waitcnt、barrier 或 issue 时移除 |
| FU class | resident instruction 的 SALU、SIMD、SIMF、LSU 目标 |
| GPR dependency | SGPR/VGPR source 和 destination readiness |
| SPR dependency | EXEC、VCC、SCC、M0 readiness |
| memory wait | LSU in-flight block，并由 done wfid 释放 |
| branch wait | branch 已发射但未 resolved |
| barrier wait | workgroup barrier arrival 和 release |
| in-flight limit | maximum outstanding instruction 或 finished-wavefront state |

使用显式 readiness equation。具体 LSU issue 条件可以是：

```text
ready = fu_lsu & valid & gpr_spr_ready & ~max_inflight & ~mem_wait & ~branch_wait & ~barrier_wait
```

对于非 LSU 单元，只移除确实不适用的 wait 项。不要把这些 owner 合并成一个无法解释的 `ready`。

## 指令影响检查表

对每类 instruction 或 uop，说明它是否改变：

- PC 或 next PC。
- active mask、predicate mask、split/join stack 或 warp status。
- integer、floating、vector 或 predicate registers。
- scoreboard 或 in-flight state。
- memory request、response、fence 或 replay state。
- barrier、CTA、CSR 或 launch-visible state。

## Bring-Up 顺序

1. Single warp、single issue、ALU-only、无 divergence。
2. Multi-warp round-robin scheduler。
3. Register writeback 和 scoreboard。
4. Active mask 和 predicated execution。
5. Branch 加简化 divergence/reconvergence state。
6. 通过 memory-path contract 接入 LSU。
7. Barrier、CTA dispatch 和完整 warp lifecycle。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 SIMT state、scheduler/fetch/decode/issue/execute/commit 边界，以及 simulator-aligned RTL contracts。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 CU RTL path、fetch 与 wavepool state、issue readiness equations、scoreboard dependency tables、EXEC/VCC/SCC/M0 ownership、FU writeback 和 trace signals。

## 常见错误

- 把 active mask 当成临时信号，而不是 core SIMT state。
- 添加 branch 或 barrier 行为，却没有 reconvergence 或 wakeup 规则。
- 把 hazard 行为隐藏在 operand read logic 里。
- 让 backpressure 依赖无关 always blocks 之间的隐式顺序。
- 只靠 waveform browsing 调试，而不是对齐 simulator/RTL trace。
