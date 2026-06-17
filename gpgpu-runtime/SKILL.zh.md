# GPGPU Runtime

> 这是 `SKILL.md` 的中文翻译版本，便于人工阅读。Codex 自动触发应以英文 `SKILL.md` 为准。

## 概述

当 host 软件、launch ABI、command submission 或 kernel entry 行为定义系统边界时，使用这个 skill。Runtime 工作应该把 testbench 驱动的 core 变成可复用 device interface，而不是把 RTL 内部信号暴露成公共 API。

## 核心规则

先定义 launch contract，再围绕它构建功能：

- program 或 module 如何加载
- kernel entry PC 如何选择
- arguments 如何 staging 和寻址
- grid、block、warp、thread、CTA ID 如何产生
- memory buffer 如何在 host 和 device 间移动
- start、completion、fence、event、cache flush 如何观察
- 哪些是 public API、backend transport、test-only scaffolding

正式 runtime 接口不应依赖 poke RTL 内部信号。

## 最小 Launch 状态机

1. 打开 device 或 simulator backend。
2. 分配或映射 device buffer。
3. 加载 program/module 并解析 kernel entry。
4. staging kernel arguments。
5. 设置 grid/block/CTA 维度和 local memory size。
6. 通过 queue 或显式 start command 提交 launch。
7. 用定义好的 status/event 路径等待 completion。
8. 拷回结果并释放资源。

这个路径可以很小，但 simulator 和 RTL test 应使用同一概念路径。

## Interface Layers

| 层次 | 职责 |
|---|---|
| public runtime API | device、buffer、module、kernel、queue、event handles |
| transport HAL | backend open/close、register read/write、host memory allocation |
| command/control plane | queue entry、doorbell、DCR/MMIO write、DMA、launch、fence、event |
| kernel ABI | entry PC、args pointer、grid/block ID、CTA state、local memory |
| tests | 一个通过 public path 运行的 launch workload |

保持这些层次分离，这样新增 backend 不需要重写 API。

## Runtime 验证

每个 runtime 修改至少需要一个：

- host API smoke test。
- simulator launch test。
- RTL-sim launch test。
- 展示 command、launch、completion ordering 的 trace。
- bad args、invalid kernel、queue full 或 timeout 的负向测试。

对 launch 相关修改，优先选择一个能同时跑 simulator 和 RTL backend 的 workload。

## 常见错误

- 把 runtime 当成脚本，而不是硬件/软件契约。
- 让 testbench-only signal poke 变成 API。
- 修改 kernel argument layout 却没有同步 simulator、RTL、runtime 和 tests。
- 加入 async queue 或 event，但没有 ordering 和 completion 语义。
- 把 cache flush 或 fence 行为藏进临时 test code。

如果需要了解更多和本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.zh.md`。它已经整理了相关 Vortex 设计文档和代码路径的要点，日常 runtime 与 launch-ABI 工作不需要重新通读整个 reference tree。
