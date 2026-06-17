---
name: gpgpu-memory-path
description: 用于设计、编辑或调试 GPGPU memory 行为，包括 LSU frontend/backend、lane masks、byte enables、outstanding requests、response demux、stores、loads、coalescing、banking、cache、MSHR、fences、stalls 或 memory traces。
---

# GPGPU Memory Path

## 概览

用于 LSU 和 memory-system 工作。先从 blocking、traceable path 开始；只有当 correctness traces 和 counters 能证明下一步有必要时，再加入 tags、response demux、coalescing、banking、cache、MSHR、fences 或 VM。

## 核心规则

每个 memory request 都必须能通过 SIMT context 追踪：

- compute core/CU ID、simt_group_id、PC 或 instruction ID
- active lane mask
- per-lane address 或 coalesced address
- byte enable 和 access width
- store data 或 load response data
- destination register 或 request tag
- response ordering rule
- relevant stall、replay、fence 或 exception reason

如果当前 trace 和 counters 不能展示某个 memory optimization 要解决的问题，就不要做该优化。

## 术语契约

Memory traces 和 tags 使用统一术语；只有命名 RTL 信号时保留源码别名。

| 统一术语 | 源码别名 | Memory-path 含义 |
|---|---|---|
| SIMT group | warp、wavefront、wave | 发出 memory operations 的 execution group |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | resident SIMT group 的 request/response identity |
| active lane mask | active mask、lane mask、thread mask、`EXEC` mask | 参与 load/store 的 lanes |
| CTA/workgroup | CTA、block、workgroup | local-memory 和 barrier scope |
| compute core/CU | core、CU、compute unit | memory-client owner |

## Frontend 和 Backend 拆分

| 区域 | 职责 |
|---|---|
| LSU frontend | AGU、address classification、byte enable、store-data alignment、fence lock、response formatting |
| Memory scheduler/backend | request queue、outstanding tag/index buffer、optional coalescing、batching、out-of-order response demux |
| Cache/bank layer | bank dispatch、hit/miss handling、MSHR、merge crossbar、flush、deadlock prevention |

在 simulator、RTL、trace 和 tests 中保持这个拆分可见。

第一版 blocking LSU 应命名自己的 FSM states，并 trace：

| 区域 | 必要证据 |
|---|---|
| issue capture | simt_group_id、PC、opcode、memory format、destination、SGPR/VGPR class |
| address generation | scalar base、vector offset、immediate、thread id、LDS base、global/LDS bit |
| lane control | active lane mask、skipped lanes、per-lane address vector |
| request | read/write enable、address、write data、write mask、tag |
| response | ack、tag、read data、destination register、writeback mask |
| completion | done simt_group_id、retire PC、memory wait release、trace event |

只有当该路径通过 load/store、masked-lane、global/LDS、SGPR/VGPR writeback 测试后，coalescing、cache、MSHR 或 VM 才应被当作实现工作，而不是推测。

## 阶段顺序

| 阶段 | 能力 | Gate |
|---|---|---|
| M0 | blocking scalar load/store | single-lane load/store trace 正确 |
| M1 | lane mask 和 byte enable | partial lane 和 access-width tests 通过 |
| M2 | vector lane memory | 每个 lane address、data、mask 都可追踪 |
| M3 | outstanding loads | tag 或 index buffer 能路由 out-of-order responses |
| M4 | coalescing | merge rate、replay、partial response 可解释 |
| M5 | bank/cache/MSHR | hit、miss、full queue、deadlock tests 存在 |
| M6 | fence/flush/VM | ordering、translation、unsupported behavior 明确 |

只有当用户要求聚焦研究且缺失假设已文档化时，才能跳过阶段。

## Non-Blocking Load 要求

任何 non-blocking load 都必须说明：

- tag 或 index-buffer allocation 和 release。
- maximum outstanding requests。
- response demux 回到 SIMT group、lane mask 和 destination 的路径。
- flush、kill、fence、exception 或 queue-full 行为。
- 捕获 deadlock 的 watchdog、assertion 或 test。

## 常见错误

- 在 working blocking LSU 之前添加 cache。
- 引入 outstanding requests 后仍假设 in-order responses。
- 做 coalescing 时丢失 per-lane writeback、byte enables 和 exception behavior。
- 在 request tag 中丢掉原始 SIMT-group/lane/destination metadata。
- 把 final kernel output 当成唯一 memory correctness check。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 LSU scheduler、memory unit、coalescer/cache/MSHR boundaries 和 full-stack memory contracts。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 MIAOW LSU opcode decoder、address calculator、op-manager FSM、simple memory model、trace signals 和 limitations。
