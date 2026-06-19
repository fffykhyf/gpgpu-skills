---
name: gpgpu-runtime
description: 用于设计、编辑或评审 GPGPU runtime、host/device launch、driver API、command queue、MMIO 或 DCR control、doorbell、DMA、buffer、module、kernel handle、kernel entry、args、grid/block/CTA/workgroup dispatch、event、fence、cache flush 或 synchronization behavior。
---

# GPGPU Runtime

## 概览

当 host software、launch ABI、command submission 或 kernel entry behavior 定义系统边界时使用本 skill。Runtime 工作应把 testbench-driven core 转换成可复用 device interface，同时不要把 RTL internals 暴露为 public API。使用 Rocket Chip 作为 boot/reset resources、debug transport、MMIO/resource descriptions、TestHarness wiring 和 RoCC-style command/response/memory/busy/interrupt accelerator control 的参考。使用 XiangShan 作为 reproducible build/run/difftest commands、reset/debug/trace/perf control surfaces、full-system images、checkpoint workflows，以及区分 debug bring-up 和 public runtime ABI 的参考。

## 核心规则

在围绕 launch 构建功能前，先定义 launch contract：

- program 或 module 如何加载
- kernel entry PC 如何选择
- arguments 如何 staged 和 addressed
- grid、CTA/workgroup、SIMT group 和 thread IDs 如何派生
- memory buffers 如何在 host 和 device 间移动
- start、completion、fence、event、cache flush 如何被观察
- reset、boot/program load、debug、fault、capability/version 和 interrupt/status paths 如何暴露
- 哪些部分是 public API、backend transport、test-only scaffolding

正式 runtime interface 不应依赖 poking internal RTL signals。

## 术语契约

Runtime API、launch records 和 ABI docs 使用统一术语；只有在 HAL boundary 保留 backend 名称。

| 统一术语 | 源码别名 | Runtime 含义 |
|---|---|---|
| SIMT group | warp、wavefront、wave | 在 CTA/workgroup 内启动的 execution group |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | launch 或 core 内的 SIMT group identity |
| active lane mask | active mask、thread mask、`tmask`、`EXEC` mask | initial 或 runtime lane participation state |
| CTA/workgroup | CTA、block、workgroup | 带 block/workgroup IDs 和 local memory 的 launch group |
| compute core/CU | core、CU、compute unit | device execution resource |

## 最小 Launch State Machine

1. 打开 device 或 simulator backend。
2. 分配或映射 device buffers。
3. 加载 program/module 并解析 kernel entry。
4. Stage kernel arguments。
5. 配置 grid/block/CTA/workgroup dimensions 和 local memory size。
6. 通过 queue 或 explicit start command 提交 launch。
7. 通过定义好的 status/event path 等待 completion。
8. 拷回结果并释放资源。

这可以很小，但 simulator 和 RTL tests 必须保持同一个概念路径。

## GPGPU-Sim Launch Model

使用 GPGPU-Sim 作为不 poke RTL internals 的 software launch path 参考：

| Runtime step | GPGPU-Sim anchor | 本地要求 |
|---|---|---|
| configure launch | `cudaConfigureCallInternal` | 捕获 grid/block、shared/local memory、stream/queue |
| stage args | `cudaSetupArgumentInternal` | 记录 argument bytes、sizes、offsets 和 alignment |
| create descriptor | `cudaLaunchInternal`、`kernel_info_t` | 解析 kernel entry 并创建稳定 kernel descriptor |
| enqueue work | `stream_operation` | 排序 memcpy、launch、event、wait 和 completion |
| backend admission | `gpu->can_start_kernel()`、launch latency | 按 capacity、latency 和 max concurrent kernels gate launch |
| CTA dispatch | `issue_block2core()` | 分配 per-core resources 并初始化 SIMT groups |

本地 runtime 可以使用比 CUDA/OpenCL 更简单的 API，但仍需要 launch config、argument staging、kernel lookup、queue operation、backend admission 和 completion semantics。

## Interface Layers

| 层 | 职责 |
|---|---|
| public runtime API | device、buffer、module、kernel、queue、event handles |
| transport HAL | backend open/close、register read/write、host memory allocation |
| command/control plane | queue entries、doorbells、DCR/MMIO writes、DMA、launch、fence、event |
| kernel ABI | entry PC、args pointer、grid/block IDs、CTA/workgroup state、local memory |
| resource/capability plane | version、device properties、memory map、queue limits、debug/perf/trace availability |
| debug/bring-up plane | reset vector 或 program-load path、debug transport、fault readout、timeout 和 success reporting |
| tests | 一个通过 public path 运行的 launch workload |

保持这些层分离，这样新增 backend 不需要重写 API。

修改 launch 行为前，先分类当前使用的 early control-plane form：

| 模式 | 允许用途 | 风险 |
|---|---|---|
| testbench C hook | unit-test setup、直接 SGPR/VGPR initialization、快速 trace regressions | 变成假的 public API |
| hard dispatcher | resource allocation、SIMT-group tags、VGPR/SGPR/LDS/GDS bases、done/deallocation | 与 compute core/CU capacity 产生 config drift |
| FPGA MMIO control | program load、register/memory init、start、done、memory-service handshake | host offsets 与 RTL decode 漂移 |

即使是最小 runtime/control plane，也必须定义 program load、state initialization、dispatch fields、start、done/status、memory service、result readback 和 cleanup。Test-only internal pokes 必须标注为 test-only。

## Rocket Chip Control-Plane 模式

使用 Rocket Chip 作为 SoC-visible runtime boundaries 的参考：

| 模式 | Rocket Chip anchor | 本地 runtime 规则 |
|---|---|---|
| boot/reset resource | `bootrom/`、reset vector、`ExampleRocketSystem` | 定义 code/data 如何进入 device，以及 reset state 中软件可以依赖什么。 |
| debug transport | `devices/debug/`、DMI/JTAG/SBA | 提供不要和 public launch API 混淆的 debug/fault/status path。 |
| resource exposure | DTS/resource binding、clock/resource files | 通过 queryable/versioned path 暴露 capabilities、queue limits、memory map 和 optional features。 |
| accelerator command | `LazyRoCC.scala` | 将 launch/control 建模为 command、response、memory access、busy、interrupt、exception 和 optional-port semantics。 |
| harness connection | `system/TestHarness.scala`、SimAXIMem/debug/success wiring | 让 simulator 和 RTL tests 通过同一组 public-facing control concepts 连接。 |

RoCC 不是 GPU runtime，但它的 command/response、busy/interrupt/fault 纪律可以直接借鉴到 GPGPU command queue 或 doorbell design。

## XiangShan Runtime 和 Difftest 模式

使用 XiangShan 作为让 run 和 debug paths 可复现的参考：

| Runtime concern | XiangShan anchor | 本地 runtime 规则 |
|---|---|---|
| build/run entry | `README.md`、`make verilog`、`make emu`、`--diff` | 用 config names 文档化 exact simulator、RTL 和 difftest launch commands。 |
| visible control state | `XSCore.scala`、`XSTile.scala` | 通过稳定边界暴露 reset、start、interrupt/status、fault、trace、perf 和 power/debug paths。 |
| full-system devices | `src/main/scala/device/` | 将 virtual devices、MMIO、memory images 和 test harness resources 与 kernel ABI 分离。 |
| interactive debug | `xspdb`、trace/debug interfaces | 提供可复现的 watch、step、status 和 trace hooks 用于 bring-up，但不要让它们变成 public ABI。 |
| reference model launch | XiangShan-NEMU `--diff` flow | Runtime tests 应能以受控方式打开或关闭 golden diff。 |
| checkpointing | NEMU checkpoint/SimPoint flow | 长 workload 在成为 PPA evidence 前应有 checkpoint 或 sampled-region support。 |

不要把 XiangShan 的 CPU boot flow 当作 GPU kernel ABI。借鉴 command、image、debug、diff、checkpoint 和 status discipline，用于 GPGPU launch path。

## Runtime 验证

每个 runtime 变更至少需要以下之一：

- host API smoke test。
- simulator launch test。
- RTL-sim launch test。
- 展示 command、launch、completion ordering 的 trace。
- bad args、invalid kernel、queue full 或 timeout 的 negative test。
- 当对应限制存在时，测试 oversized CTA/workgroup、max concurrent kernels 或 backend admission failure。
- public resources、queue limits、memory maps 或 optional features 变化时，增加 capability/version test。
- 当对应路径存在时，增加 invalid command、memory fault、timeout 或 forced interrupt 的 debug/fault/status test。

对于 launch 相关变更，优先选择一个同时跑过 simulator 和 RTL backend 的 workload。

## 常见错误

- 把 runtime 当成脚本，而不是 hardware/software contract。
- 让 testbench-only signal pokes 变成 API。
- 修改 kernel argument layout 却不更新 simulator、RTL、runtime 和 tests。
- 添加 async queues 或 events，却没有 ordering 和 completion semantics。
- 把 launch latency、max concurrent kernels 或 resource admission 隐藏在 backend-only constants 中，而不是 config/runtime-visible behavior。
- 把 cache flush 或 fence behavior 隐藏在临时 test code 中。
- 添加 MMIO registers，却没有 owner、reset value、side effect、capability/version 和 test-harness coverage。
- 把 debug/JTAG/DMI-style bring-up paths 当成 public kernel launch API。
- 直接复制 XiangShan reset/boot/debug mechanics 到 GPU runtime，而不是定义 kernel descriptor、queue/doorbell、completion、fault、trace 和 diff contract。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 handle-based runtime APIs、command processor control plane、kernel entry、CTA/workgroup dispatch 和 launch DCR programming。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 testbench soft dispatch、hard resource dispatch、FPGA AXI-lite control registers、Xilinx SDK command flow，以及 test hooks 和 public runtime contracts 的边界。

若想了解与本 skill 相关的 GPGPU-Sim 背景，请阅读本目录下的 `gpgpusim_local.md`。它说明 CUDA/OpenCL runtime interception、launch stack handling、`kernel_info_t`、stream operations、functional/performance mode selection 和 launch admission。

若想了解与本 skill 相关的 Rocket Chip 背景，请阅读 `../../ref/skillref/rocket.md`，必要时查看 `../../ref_submodule/rocket-chip/src/main/scala/tile/LazyRoCC.scala`、`system/ExampleRocketSystem.scala`、`system/TestHarness.scala`、`bootrom/`、`devices/debug/` 和 `resources/`。

若想了解与本 skill 相关的 XiangShan 背景，请阅读本目录下的 `xiangshan_local.md`。它说明 XiangShan build/run/difftest flow、reset/debug/trace/perf ports、virtual devices、full-system images、`xspdb`、checkpointing，以及这些思想如何翻译到 GPGPU runtime boundary。
