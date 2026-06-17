---
name: gpgpu-runtime
description: 用于设计、编辑或评审 GPGPU runtime、host/device launch、driver API、command queue、MMIO 或 DCR control、doorbell、DMA、buffer、module、kernel handle、kernel entry、args、grid/block/CTA/workgroup dispatch、event、fence、cache flush 或 synchronization behavior。
---

# GPGPU Runtime

## 概览

当 host software、launch ABI、command submission 或 kernel entry behavior 定义系统边界时使用本 skill。Runtime 工作应把 testbench-driven core 转换成可复用 device interface，同时不要把 RTL internals 暴露为 public API。

## 核心规则

在围绕 launch 构建功能前，先定义 launch contract：

- program 或 module 如何加载
- kernel entry PC 如何选择
- arguments 如何 staged 和 addressed
- grid、CTA/workgroup、SIMT group 和 thread IDs 如何派生
- memory buffers 如何在 host 和 device 间移动
- start、completion、fence、event、cache flush 如何被观察
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

## Interface Layers

| 层 | 职责 |
|---|---|
| public runtime API | device、buffer、module、kernel、queue、event handles |
| transport HAL | backend open/close、register read/write、host memory allocation |
| command/control plane | queue entries、doorbells、DCR/MMIO writes、DMA、launch、fence、event |
| kernel ABI | entry PC、args pointer、grid/block IDs、CTA/workgroup state、local memory |
| tests | 一个通过 public path 运行的 launch workload |

保持这些层分离，这样新增 backend 不需要重写 API。

修改 launch 行为前，先分类当前使用的 early control-plane form：

| 模式 | 允许用途 | 风险 |
|---|---|---|
| testbench C hook | unit-test setup、直接 SGPR/VGPR initialization、快速 trace regressions | 变成假的 public API |
| hard dispatcher | resource allocation、SIMT-group tags、VGPR/SGPR/LDS/GDS bases、done/deallocation | 与 compute core/CU capacity 产生 config drift |
| FPGA MMIO control | program load、register/memory init、start、done、memory-service handshake | host offsets 与 RTL decode 漂移 |

即使是最小 runtime/control plane，也必须定义 program load、state initialization、dispatch fields、start、done/status、memory service、result readback 和 cleanup。Test-only internal pokes 必须标注为 test-only。

## Runtime 验证

每个 runtime 变更至少需要以下之一：

- host API smoke test。
- simulator launch test。
- RTL-sim launch test。
- 展示 command、launch、completion ordering 的 trace。
- bad args、invalid kernel、queue full 或 timeout 的 negative test。

对于 launch 相关变更，优先选择一个同时跑过 simulator 和 RTL backend 的 workload。

## 常见错误

- 把 runtime 当成脚本，而不是 hardware/software contract。
- 让 testbench-only signal pokes 变成 API。
- 修改 kernel argument layout 却不更新 simulator、RTL、runtime 和 tests。
- 添加 async queues 或 events，却没有 ordering 和 completion semantics。
- 把 cache flush 或 fence behavior 隐藏在临时 test code 中。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 handle-based runtime APIs、command processor control plane、kernel entry、CTA/workgroup dispatch 和 launch DCR programming。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 testbench soft dispatch、hard resource dispatch、FPGA AXI-lite control registers、Xilinx SDK command flow，以及 test hooks 和 public runtime contracts 的边界。
