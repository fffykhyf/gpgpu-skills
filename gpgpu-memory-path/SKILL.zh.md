# GPGPU Memory Path

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

这个 skill 用于 LSU 和 memory-system 工作。先建立 blocking、可 trace 的路径；只有 correctness trace 和 counter 证明有必要时，才加入 tag、response demux、coalescing、banking、cache、MSHR、fence 或 VM。

## 核心规则

每个 memory request 都必须能按 SIMT 上下文追踪：

- core ID、warp ID、PC 或 instruction ID
- active lane mask
- 每 lane address 或 coalesced address
- byte enable 和 access width
- store data 或 load response data
- destination register 或 request tag
- response ordering rule
- 相关 stall、replay、fence 或 exception reason

如果当前 trace 和 counter 无法显示某个 memory 优化解决的问题，就不要做这个优化。

## Frontend And Backend 拆分

| 区域 | 职责 |
|---|---|
| LSU frontend | AGU、address classification、byte enable、store-data alignment、fence lock、response formatting |
| Memory scheduler/backend | request queue、outstanding tag/index buffer、optional coalescing、batching、out-of-order response demux |
| Cache/bank layer | bank dispatch、hit/miss、MSHR、merge crossbar、flush、deadlock prevention |

这个拆分必须在 simulator、RTL、trace 和测试中保持可见。

## 阶段顺序

| 阶段 | 能力 | Gate |
|---|---|---|
| M0 | blocking scalar load/store | 单 lane load/store trace 正确 |
| M1 | lane mask 和 byte enable | partial lane 和 access-width 测试通过 |
| M2 | vector lane memory | 每 lane address、data、mask 可追踪 |
| M3 | outstanding loads | tag 或 index buffer 能路由 out-of-order response |
| M4 | coalescing | merge rate、replay、partial response 可解释 |
| M5 | bank/cache/MSHR | hit、miss、queue full、deadlock 测试存在 |
| M6 | fence/flush/VM | ordering、translation 和 unsupported 行为明确 |

只有当用户要求聚焦研究，并且缺失假设已记录时，才跳过阶段。

## Non-Blocking Load 要求

任何 non-blocking load 都必须说明：

- tag 或 index-buffer 的分配和释放。
- 最大 outstanding request 数量。
- response demux 如何回到 warp、lane mask 和 destination。
- flush、kill、fence、exception 或 queue-full 时的行为。
- 捕获 deadlock 的 watchdog、assertion 或测试。

## 常见错误

- 在 working blocking LSU 前加入 cache。
- 引入 outstanding request 后仍假设 in-order response。
- coalescing 时没有保持 per-lane writeback、byte enable 和 exception 行为。
- 在 request tag 中丢失原始 warp/lane/destination 元数据。
- 把最终 kernel output 当作唯一 memory 正确性检查。

如果需要了解更多和本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.zh.md`。它已经整理了相关 Vortex 设计文档和代码路径的要点，日常 LSU 与 memory-system 工作不需要重新通读整个 reference tree。
