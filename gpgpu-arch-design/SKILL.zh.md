# GPGPU 架构设计

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

在本地 GPGPU 开发中，把这个 skill 当作顶层护栏使用。它要求工作始终围绕一个可运行、可观测的路径推进，避免 ISA、RTL、runtime 和性能优化混在一起失控演进。

## 核心规则

在修改或提出任何 GPGPU 功能前，先把任务归类到一个或多个层次：

| 层次 | 典型产物 | 必须回答的问题 |
|---|---|---|
| ISA | 指令语义、编码、汇编规则 | 架构状态会怎样变化？ |
| Simulator | 功能模型、周期模型、golden trace | 参考行为是什么？ |
| RTL | 流水线、SIMT core、LSU、cache、互连 | valid-ready 和 stall 契约是什么？ |
| Runtime | launch ABI、host/device 契约、buffer | 软件如何启动和观察任务？ |
| Tests | smoke test、trace diff、回归测试 | 什么能证明这一阶段可工作？ |
| Evaluation | counter、日志、PPA 报告 | 哪个指标能支撑这个修改？ |
| Docs | 架构笔记、设计决策 | 下一个 agent 需要知道什么？ |

不要隐式修改多个层次。必须说清楚受影响层次，并为每个层次补上最小验证路径。

## 阶段顺序

除非用户明确要求只做某个局部调查，否则按以下顺序推进：

1. 定义项目骨架、ISA 草图、SIMT 状态和集中配置。
2. 在复杂 RTL 前先建立或更新 simulator/golden model。
3. 实现最小 SIMT core：warp state、active mask、scheduler、register file、ALU、commit。
4. 加入 memory path：先做 blocking LSU，再做 lane mask 和 byte enable，最后再考虑 coalescing/cache。
5. 定义 runtime 或 testbench launch contract：load program、load args、start、done、read result。
6. 在性能调优前加入 counter：cycles、instructions、warp stalls、memory stalls、load/store 数量。
7. 只有 trace 和 counter 显示瓶颈后，才加入 memory hierarchy。
8. 基础 loop 稳定后，再进入 synthesis、FPGA、PPA、VM、tensor 或软件生态工作。

## 设计工作必须输出

当用户要求设计或扩展 GPGPU 时，输出：

- 范围：受影响层次和非目标。
- 状态契约：PC、active mask、warp state、register、memory，必要时包括 launch state。
- 执行路径：simulator 行为、RTL 模块边界、runtime/test 入口。
- 验证：最小 smoke test、trace diff 计划、所需 counter。
- 延后列表：明确不在当前阶段处理的高级特性。

## 常见错误

- 没有 reference model 就开始写 RTL。
- 在最小 SIMT loop 可调试前加入 cache、VM、tensor、OpenCL 或 HIP。
- 把测试当作最终输出检查，而不是可追踪的行为检查。
- 在多个无关文件中硬编码 core、warp、lane、register 或 memory 大小。
- 让 testbench 直接 poke 内部信号的方式变成永久 runtime 接口。
