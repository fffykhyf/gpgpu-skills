---
name: gpgpu-arch-design
description: 用于规划、分阶段实现或评审 GPGPU 架构，范围包括 ISA、SIMT 执行、模拟器、RTL、runtime 启动、配置、测试、计数器、内存层级、PPA、FPGA bring-up 或路线图决策。
---

# GPGPU 架构设计

## 概览

将本 skill 作为本地 GPGPU 工作的顶层护栏。GPGPU 是完整系统工程，因此架构工作必须说明 ISA、模拟器、RTL、runtime、kernel ABI、配置、测试和 PPA 证据如何保持一致。

## 核心规则

在修改或提出任何 GPGPU 功能前，先给出层级影响表和分阶段验证路径。

| 层级 | 典型产物 | 必须回答的问题 |
|---|---|---|
| ISA | 指令语义、编码、CSR/DCR 状态 | 哪些架构状态会改变？ |
| 模拟器 | functional model、cycle model、golden trace | 可执行参考是什么？ |
| RTL | SIMT core、LSU、cache、CP、interconnect | valid-ready 和 stall 契约是什么？ |
| Runtime | device、buffer、queue、launch、event、fence | host 软件如何启动并观察工作？ |
| Kernel ABI | entry PC、args、grid/block/CTA/workgroup IDs | device 代码假设了什么？ |
| Config | 私有旋钮、ABI 常量、生成头文件 | 哪些值跨层可见？ |
| Tests | smoke、trace diff、regression、backend matrix | 什么能证明这一阶段可用？ |
| Evaluation | counters、logs、SAIF、synthesis reports | 哪个指标支撑这个变化？ |

不要静默修改多个层级。列出每个受影响层级、每个契约的 owner，以及证明它仍然工作的最小 gate。

## 术语契约

新的设计和文档使用统一术语；只有在引用具体参考实现时保留源码原名。

| 统一术语 | 源码别名 | 含义 |
|---|---|---|
| SIMT group | warp、wavefront、wave | 共享 PC、scheduler residency 和 active lane mask 的 threads 或 work-items |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | 一个 resident SIMT group 的身份 |
| active lane mask | active mask、thread mask、`tmask`、`EXEC` mask | SIMT group 的 per-lane participation mask |
| CTA/workgroup | CTA、block、workgroup | 包含一个或多个 SIMT groups 的 launch group |
| compute core/CU | core、CU、compute unit | 拥有 SIMT groups 和 execution resources 的硬件单元 |

保持 `simt_group_width`、`active_mask_width`、`physical_simd_width`、`resident_simt_groups` 和 `test_thread_count` 分开记录。

## 必要契约

每个架构设计都应包含：

- Objective：正在测试的一个能力或假设。
- Non-goals：明确不做的高级功能。
- State contract：PC、active lane mask、SIMT group state、registers、memory、CSR/DCR、launch state。
- Config contract：将每个参数分类为 hardware-private、simulator-private、HW/SW ABI、test-only 或 debug-only。
- Launch contract：program image、kernel entry、args、grid/block dimensions、start、done、result、synchronization path。
- Test gate：simulator smoke、RTL trace diff、runtime launch test、counter check 或 PPA report。
- Prototype credibility target：instruction unit tests、external golden trace、RTL simulation、FPGA smoke、benchmark run、synthesis report 或 ASIC estimate。
- Implementation anchors：说明哪个模块或计划模块拥有该声明。

对于需要落成可信 prototype 的架构方案，还要记录：

| 项 | 必填内容 |
|---|---|
| ISA scope | 已支持、计划支持、明确不支持的指令或功能 |
| CU organization | resident SIMT-group slots、issue width、active-mask width、physical SIMD width、SGPR/VGPR/LDS resources |
| Implementation anchors | fetch、wavepool、decode、issue、scoreboard、exec state、FU、LSU、dispatcher 或 control-plane owner |
| Evidence path | unit test、external oracle trace、RTL tracemon diff、FPGA control path、PPA report |
| Credibility caveat | relaxed frequency、area、power、tooling、ISA、runtime、memory hierarchy 或 benchmark assumptions |

不要把 SIMT-group width、active-mask width、physical SIMD width、resident SIMT-group slots 和 test thread count 混成一个模糊的 "lane count"。

## 阶段顺序

1. 定义项目骨架、ISA sketch、SIMT state、configuration boundary 和最小 launch path。
2. 在复杂 RTL 之前建立 simulator 或 golden trace。
3. 实现最小 SIMT core：SIMT group state、active lane mask、scheduler、register file、ALU、commit。
4. 分阶段加入 memory：blocking LSU、lane masks 和 byte enables、outstanding tags、response demux，然后再 coalescing/cache。
5. 用 runtime 或 launch contract 替代 testbench pokes：load program、load args、start、wait、copy result。
6. 在调优前加入 counters：cycles、instructions、SIMT-group stalls、scoreboard stalls、memory stalls、load/store counts。
7. 只有在基本循环可调试后，才加入 cache、VM、tensor、graphics、FPGA 或软件生态工作。
8. 只有 correctness gates 通过后才使用 PPA。

## Skill 路由

当任务主要集中在某个边界时，使用更窄的 skill：

| 任务形态 | 使用 |
|---|---|
| 参数或 ABI 变更 | `gpgpu-config` |
| 参考行为或 trace mismatch | `gpgpu-golden-sim` |
| SIMT RTL 状态或 pipeline | `gpgpu-rtl-simt-core` |
| LSU、cache、coalescing、memory ordering | `gpgpu-memory-path` |
| Host/device launch、queue、event、kernel entry | `gpgpu-runtime` |
| Performance、power、area、timing | `gpgpu-ppa-evaluation` |

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 RTL、simulator、runtime、ABI、config、tests 和 PPA 之间的 full-stack contract。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 MIAOW paper scope、CU source anchors、trace/test loop、FPGA control path，以及与架构工作相关的 prototype credibility caveats。

## 常见错误

- 只画 RTL block diagram，却遗漏 runtime、config、tests 或 counters。
- 把 launch ABI 和 configuration 当成脚本细节，而不是架构契约。
- 在最小 SIMT loop 可 trace 之前加入 cache、VM、tensor、OpenCL、HIP、Vulkan 或 FPGA bring-up。
- 让 testbench-only internal pokes 变成永久 runtime interface。
- 一次改变多个变量，然后把结果称为架构结论。
