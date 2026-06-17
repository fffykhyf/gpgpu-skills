# GPGPU 架构设计

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

在本地 GPGPU 工作中，把这个 skill 当作顶层护栏使用。GPGPU 是全栈系统，因此架构设计必须说明 ISA、simulator、RTL、runtime、kernel ABI、配置、测试和 PPA 证据如何保持一致。

## 核心规则

修改或提出任何 GPGPU 功能前，先输出 layer impact table 和分阶段验证路径。

| 层次 | 典型产物 | 必须回答的问题 |
|---|---|---|
| ISA | 指令语义、编码、CSR/DCR 状态 | 架构状态会怎样变化？ |
| Simulator | 功能模型、周期模型、golden trace | 可执行参考是什么？ |
| RTL | SIMT core、LSU、cache、CP、互连 | valid-ready 和 stall 契约是什么？ |
| Runtime | device、buffer、queue、launch、event、fence | host 软件如何启动和观察任务？ |
| Kernel ABI | entry PC、args、grid/block/CTA ID | device 侧代码依赖什么？ |
| Config | 私有参数、ABI 常量、生成头文件 | 哪些值会跨层可见？ |
| Tests | smoke、trace diff、regression、backend matrix | 什么证明这一阶段可工作？ |
| Evaluation | counter、log、SAIF、综合报告 | 哪个指标支撑这个修改？ |

不要隐式修改多个层次。必须说明每个受影响层次、契约所有者，以及证明它仍然工作的最小 gate。

## 必须定义的契约

每次架构设计都应包含：

- Objective：本轮只验证一个能力或假设。
- Non-goals：明确不做的高级能力。
- State contract：PC、active mask、warp state、register、memory、CSR/DCR 和 launch state。
- Config contract：把参数归类为 hardware-private、simulator-private、HW/SW ABI、test-only 或 debug-only。
- Launch contract：program image、kernel entry、args、grid/block 维度、start、done、result 和同步路径。
- Test gate：simulator smoke、RTL trace diff、runtime launch test、counter check 或 PPA report。

## 阶段顺序

1. 定义项目骨架、ISA 草图、SIMT 状态、配置边界和最小 launch 路径。
2. 在复杂 RTL 前建立 simulator 或 golden trace。
3. 实现最小 SIMT core：warp state、active mask、scheduler、register file、ALU、commit。
4. 分阶段加入 memory：blocking LSU、lane mask/byte enable、outstanding tag、response demux，最后才是 coalescing/cache。
5. 用 runtime 或 launch contract 替代 testbench 直接 poke：load program、load args、start、wait、copy result。
6. 在调优前加入 counter：cycles、instructions、warp stalls、scoreboard stalls、memory stalls、load/store 数量。
7. 基础 loop 可 trace 后，再考虑 cache、VM、tensor、graphics、FPGA 或软件生态。
8. 只有 correctness gate 通过后，PPA 结论才有意义。

## Skill 路由

如果任务主要落在某个边界，使用更窄的 skill：

| 任务形态 | 使用 |
|---|---|
| 参数或 ABI 变更 | `gpgpu-config` |
| 参考行为或 trace mismatch | `gpgpu-golden-sim` |
| SIMT RTL 状态或流水线 | `gpgpu-rtl-simt-core` |
| LSU、cache、coalescing、memory ordering | `gpgpu-memory-path` |
| host/device launch、queue、event、kernel entry | `gpgpu-runtime` |
| performance、power、area、timing | `gpgpu-ppa-evaluation` |

## 常见错误

- 只画 RTL 模块图，漏掉 runtime、config、tests 或 counters。
- 把 launch ABI 和配置当作脚本细节，而不是架构契约。
- 在最小 SIMT loop 可 trace 前加入 cache、VM、tensor、OpenCL、HIP、Vulkan 或 FPGA bring-up。
- 让 testbench 内部信号 poke 变成永久 runtime 接口。
- 同时改变多个变量，却把结果称为架构结论。

如果需要了解更多和本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.zh.md`。它已经把相关 Vortex 设计文档和代码路径的要点整理进去，日常架构工作不需要重新通读整个 reference tree。
