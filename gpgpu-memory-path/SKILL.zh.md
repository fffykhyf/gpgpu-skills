# GPGPU Memory Path

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

这个 skill 用于 LSU 和 memory-system 工作。先建立 blocking、可 trace 的 memory path；只有 counter 和 trace 说明必要时，才加入 coalescing、banking、cache 和 MSHR。

## 核心规则

每个 memory request 都必须能按 SIMT 上下文追踪：

- core 和 warp ID
- PC 或 instruction ID
- active lane mask
- 每个参与 lane 的 address，或 coalesced address
- byte enable
- store data 或 load response data
- request tag 或 destination register
- 相关 stall、replay 或 response reason

如果当前 trace 和 counter 无法显示某个 memory 优化解决的问题，就不要做这个优化。

## 阶段顺序

1. 支持 aligned word loads/stores 的 blocking LSU。
2. lane mask 和 byte enable 支持。
3. 带简单 tag 的 outstanding request tracking。
4. load response demux 和 writeback trace。
5. memory stall counter 和 bandwidth counter。
6. 针对同一 cache line 或兼容 lane request 的 coalescing。
7. banking 和 arbitration。
8. cache、non-blocking cache、MSHR、TLB、VM 和 fence。

只有当用户明确要求聚焦研究，并且缺失假设已记录时，才跳过阶段。

## 设计检查清单

对每个 memory 功能回答：

- 问题是 bandwidth、latency、serialization、bank conflict、replay、ordering 还是 coherence？
- 行为是架构行为，还是纯时序优化？
- response ordering 规则是什么？
- 部分 lane inactive 时会发生什么？
- partial store 或 unaligned access 时会发生什么？
- 哪个 counter 能显示改善或退化？
- 哪个 trace 能暴露错误 request 或 response？

## 常见错误

- 在 working blocking LSU 之前加入 cache。
- coalescing request 时没有保持 per-lane writeback 和异常行为。
- 在 trace 中丢失 byte-enable 信息。
- 引入 outstanding request 后仍假设 in-order response。
- 把最终 kernel output 当作唯一 memory 正确性检查。
