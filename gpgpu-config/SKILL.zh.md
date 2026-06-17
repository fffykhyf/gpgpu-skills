---
name: gpgpu-config
description: 用于添加、编辑或评审 GPGPU parameters、generated config、hardware-private knobs、simulator-private knobs、HW/SW ABI constants、CSR 或 DCR maps、memory maps、kernel ABI values、device capabilities、backend config drift 或 hard-coded core/warp/thread/cache values。
---

# GPGPU Config

## 概览

当某个值可能在 RTL、simulator、runtime、kernel、tests 或 PPA scripts 之间漂移时使用本 skill。配置工作不只是把数字换成 macros；它是在判断哪些值是 private implementation knobs，哪些值是 visible contracts。

## 核心规则

修改任何参数前先分类：

| 类别 | 含义 | 典型例子 |
|---|---|---|
| hardware-private | 只属于 RTL 和 synthesis microarchitecture | queue depth、cache MSHR size、pipeline latency |
| simulator-private | 只属于 model 的 debug 或 timing knob | simulator verbosity、synthetic latency |
| HW/SW ABI | 对 RTL 和软件可见 | CSR/DCR map、memory map、kernel args、capability bits |
| test-only | 仅限 tests 或 fixtures | small smoke-test memory size |
| debug-only | instrumentation、trace、assertions | trace level、watchdog timeout |

HW/SW ABI 值需要 single source of truth，并通过 RTL、simulator、runtime、kernel 和 tests 验证。

对于常见 GPGPU 值族，先按下面方式分类：

| 值族 | 必要分类 |
|---|---|
| wavefront and mask sizes | architectural limit、physical SIMD width、test thread count 或 FPGA prototype limit |
| SGPR/VGPR/LDS/GDS counts | physical resource、dispatch allocation unit 或 test fixture value |
| dispatcher fields | HW/SW ABI、resource-private 或 debug-only |
| MMIO/control offsets | HW/SW ABI，需要同步 RTL decode、host header、tests、docs |
| unit-test config format | 带 parser validation 的 test ABI |
| conditional build flags | interface-changing、implementation-only、debug-only 或 FPGA-only |

## 变更检查表

每个 config 变更都要：

- 说明参数类别。
- 找出 single source of truth。
- 列出 generated 或 synchronized consumers。
- 审计 Verilog `define`、Verilog parameter、C `#define`、scripts、unit-test config、FPGA scripts、generated headers 和 docs 中的重复出现。
- 说明 public capability、version 或 query output 是否变化。
- 移除重复 hard-coded copies。
- 至少测试一个 small config 和一个 target config。
- 如果该值影响 evaluation，更新 PPA config IDs。

## 边界规则

- Hardware-private knobs 可以调优实现，但不能泄漏到 public runtime headers。
- ABI constants 必须通过 generated headers、documented maps 或 explicit capability queries 对所有 consumers 可见。
- Debug/test knobs 不应变成永久 architecture assumptions。
- Derived values 应从 source values 生成，而不是手动复制。
- 修改 visible config 但不更新 tests 和 capability reporting 是 bug。
- 如果存在 MMIO map，修改任何 offset 前先列出 RTL decode path、host C/C++ constants、tests 和 documentation consumer。
- 如果 unit-test config format 变化，同步更新 parser validation、generators、fixtures 和 trace/regression expectations。
- 如果 conditional build flag 会改变 interface，说明它是 public、FPGA-only、debug-only 还是 test-only。

## Drift Signals

看到以下情况时立即使用本 skill：

- lane、warp、core、register、cache 或 memory sizes 被复制到多个文件。
- simulator 和 RTL 使用不同 constants。
- runtime 从 build flags 猜测 hardware capability。
- tests 只在一个 hard-coded configuration 下通过。
- PPA results 的 config 无法重建。

## 常见错误

- 把每个数字都当成同一种 macro。
- 混合 microarchitecture knobs 和 software ABI constants。
- 更新 RTL，却让 simulator、runtime 或 tests 保留旧值。
- 修改 memory maps 或 CSR/DCR numbers，却没有 capability 或 version story。
- 修改 parameterized logic 后只跑 default config。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 generated config/type sources、ABI-visible values、DCR/capability contracts 和 backend config synchronization。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 global definitions、dispatcher parameters、FPGA MMIO registers、Xilinx SDK offsets、unit-test config files 和 SIAGen workload parameters 中分散的 constants。
