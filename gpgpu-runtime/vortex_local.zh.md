# GPGPU Runtime 的 Vortex 本地参考

本文件展开 `gpgpu-runtime` skill 需要的 Vortex 参考，覆盖 public runtime handles、command submission、module/kernel loading、kernel entry ABI、command processor control、CTA/KMU dispatch 和 host/device synchronization。

## 这个 skill 应该从 Vortex 学什么

Vortex 把 user-facing runtime、backend transport、RTL internals 分开。public API 使用 device、buffer、queue、event、module、kernel handles。backend 拥有 MMIO/DMA/platform 细节。command processor 和 KMU 把 queue commands 转成 DCR writes、DMA、launch、completion、events、fences、cache maintenance。

本地项目应复制这些 contract：

- kernel launch 是 state machine，不是 testbench poke；
- kernel entry PC 和 argument pointer 是 ABI；
- grid/block/CTA dimensions 对 runtime 和 core 都可见；
- completion、fence、event、cache flush 必须有显式 ordering；
- public runtime header 不应暴露 private RTL internals。

## 参考阅读顺序

| Path | 关注点 |
|---|---|
| `ref/skillref/vortex.md` | runtime/launch lessons。 |
| `ref_submodule/vortex/docs/designs/vortex_runtime_api.md` | public async runtime API：device、buffer、queue、event、module、kernel。 |
| `ref_submodule/vortex/docs/designs/command_processor_control_plane.md` | command rings、doorbells、queue completion、DMA、DCR、launch、fence、event、cache flush。 |
| `ref_submodule/vortex/docs/designs/kernel_entry_and_dispatch.md` | kernel entry PC、multi-entry `.vxbin`、`VXSYMTAB`、argument handoff、startup ABI。 |
| `ref_submodule/vortex/docs/designs/cta_clustering_and_dispatch.md` | KMU grid walk、CTA dispatch、cluster dimensions、CTA-visible state。 |
| `ref_submodule/vortex/docs/testing.md` | simx/rtlsim 下 runtime-facing tests。 |

## Public Runtime Surface

Vortex runtime headers 位于：

- `ref_submodule/vortex/sw/runtime/include/vortex2.h`
- `ref_submodule/vortex/sw/runtime/include/vortex.h`

重要 API 分类：

- device handles：open/close、query capabilities、backend state；
- buffer handles：allocate/reserve、map/copy、access permissions、release；
- queue handles：ordered submission 和 asynchronous completion；
- event handles：completion markers 和 synchronization；
- module handles：loaded `.vxbin` device image 和 symbol table；
- kernel handles：module 内 resolved kernel entry PC；
- launch arguments：raw argument blob 或 staged argument buffer；
- synchronization：wait、fence、cache flush、callback/event semantics。

小 runtime 也要保留 public/private split。public API 可以很小，但不应要求 caller 知道 RTL 内部 signal name 或 CP implementation detail。

## Device 与 Command Processor Runtime

`ref_submodule/vortex/sw/runtime/common/device.cpp` 是 device-level state 和 CP interaction 的 common owner。

重要行为：

- CP initialization 分配 command-ring storage、queue head/completion state，并写 CP registers。
- device capabilities 通过 CP-visible capability words 读取，再由 shared helpers 解码。runtime-visible capabilities 不从随机 build flags 猜。
- `cp_submit_cl` 把 command-list entries 写入 ring，在 doorbell 前使用 release fence，写 CP doorbell，然后 poll completion sequence state（例如 `Q_SEQNUM`）。
- 在 CP-only-DMA backend 上，device write/read 可以通过 CP DMA，因此 runtime 不应假设 host 可直接访问 device memory。

本地 lesson：command submission 需要显式 producer/consumer protocol：ring space、entry write、ordering fence、doorbell、completion、error/timeout。

## Queue Launch Path

`ref_submodule/vortex/sw/runtime/common/queue.cpp` 是实际 launch path 参考。

kernel launch enqueue 的关键步骤：

- 校验 device、queue、kernel、dimensions、argument inputs；
- retain kernel/module，保证 queued work 拥有期间对象有效；
- 复制或 stage raw argument blob；
- normalize grid、block、cluster dimensions；
- 查询 device capabilities，例如 threads、warps、cores、local memory、feature limits；
- 计算 block size、warp stepping 等 derived launch parameters；
- 写 launch DCR：startup address、kernel entry、startup argument、block/grid dimensions、local memory size、block size、warp steps、cluster dimensions；
- 通过 queue/CP path 提交 command list；
- completion 或 failure 后释放 staged resources。

本地 runtime work 即使第一个 backend 是 simulator，也不要跳过 DCR/launch record。它让 sim 和 RTL 共享同一个 conceptual launch ABI。

## Module 与 Kernel Loading

`ref_submodule/vortex/sw/runtime/common/module.cpp` 描述 `.vxbin` module format 和 kernel resolution。

`.vxbin` layout：

- 8-byte little-endian `min_vma`
- 8-byte little-endian `max_vma`
- binary payload
- optional symbol-table footer：
  - concatenated string blob
  - `{ name_off, name_len, pad, pc }` entries
  - `n_symbols`
  - magic bytes `VXSYMTAB`

`Module::load_bytes()` 会：

- 校验 header 和 VMA range；
- 从文件尾检测并解析 optional `VXSYMTAB` footer；
- 把 image VMA range reserve 为 device buffer；
- 标记 code/data read-only、BSS read-write；
- 用 `dev_write` 上传 binary payload；
- zero BSS region；
- 把 footer entries 暴露为 named kernel symbols；
- 没有 footer 时 fallback 到 `min_vma` 处单个 `main` entry；
- 对 single-entry footer image 也在必要时暴露 `main`，兼容 legacy tests。

`Kernel` 缓存 resolved PC 并持有 module reference，也能从 device capabilities 查询 max block size。关键 lesson：kernel entry resolution 是 runtime state，不是 testbench compile-time constant。

## Kernel Binary Tooling

`ref_submodule/vortex/sw/kernel/scripts/vxbin.py` 从 ELF 生成 `.vxbin`：

- 用 `readelf -l` 找 min/max loadable VMA；
- 读取 `_edata` 和 `_end`，覆盖 initialized data 和 BSS extent；
- 用 `objcopy -O binary` 提取 binary payload；
- pad payload 到 `_edata`，让 runtime 区分 binary data 和 BSS；
- 写 `min_vma`、`max_vma`、payload、optional `VXSYMTAB`；
- 查找名为 `__vx_kentry_<kernel>` 的 kernel entry stubs；
- 把 `kernel_main` 映射成 public name `main`；
- 每个 footer entry 写 name offset/length 和 PC。

本地如果引入 multi-kernel modules，也应让 runtime 通过 module format 解析 named kernel entry PC，而不是 host 硬编码。

## Kernel Startup ABI

`ref_submodule/vortex/sw/kernel/src/vx_start.S` 是 kernel entry ABI 参考。

KMU-enabled launch 下：

- `_start` alias 到 `__vx_cta_entry`；
- KMU 把每个 CTA/warp launch 到 startup address；
- `__vx_cta_entry` 在 VM enable 时配置 SATP；
- 初始化 `gp`、stack pointer、optional TLS、global constructors；
- 从 `VX_CSR_CTA_ENTRY` 读取 selected kernel entry PC；
- 从 `VX_CSR_MSCRATCH` 读取 kernel-argument pointer；
- 通过 `jalr` 调用 selected kernel；
- 用 `wsync` drain pending work；
- 用 `tmc x0` shutdown warp；
- reused CTA warp 会重新进入固定 per-CTA dispatch window，重新加载 entry 和 args。

本地最小 kernel ABI 应定义：

- kernel 从哪里开始；
- args 如何到达 kernel；
- stack/TLS/global init 如何处理或明确省略；
- warp/thread 如何终止；
- 哪些 CSR 或等价状态暴露 CTA IDs 和 dimensions。

## Command Processor RTL

command processor RTL 位于 `ref_submodule/vortex/hw/rtl/cp/`。

关键文件：

- `VX_cp_pkg.sv`：command opcodes、command structures、queue state、register offsets、shared CP types。
- `VX_cp_core.sv`：CP regfile、command fetch、command execution engines、arbiters、host/device AXI interactions、GPU interface、queue progress、completion signaling。

command processor 设计文档描述 command classes：

- register/DCR writes；
- DMA transfers；
- kernel launch；
- fence/wait；
- event operations；
- cache flush；
- queue completion 和 doorbell。

早期本地项目不需要完整 Vortex CP，但要保留 logical roles。tiny runtime 可以直接提交单个 launch command，但仍需要 start、completion、error、ordering semantics。

## KMU 与 CTA Dispatch

launch command 最终到达：

- `ref_submodule/vortex/hw/rtl/VX_kmu.sv`
- `ref_submodule/vortex/hw/rtl/core/VX_cta_dispatch.sv`

KMU 保存 DCR-programmed launch state：

- startup address；
- kernel entry address；
- argument pointer；
- block dimensions；
- grid dimensions；
- local memory size；
- block size；
- warp stepping in X/Y/Z；
- cluster dimensions。

CTA dispatch 把 grid/block/cluster state 映射成 core 可见的 warp records。SimX 在 `sim/simx/scheduler.cpp` 中 mirror：activation 时把 CTA metadata 复制到 per-warp CSR state。

这是 runtime 与 SIMT core 的边界。如果 kernel 看到错误 `blockIdx`、`threadIdx`、`gridDim` 或 args，应先 debug launch/DCR/CTA path，而不是先怀疑 core ALU 或 memory pipeline。

## Capability 与 Config Boundary

`ref_submodule/vortex/sw/runtime/common/caps.h` 解码从 CP register file 读取的 runtime-visible capability words：

- number of threads、warps、cores、sockets、clusters；
- issue width；
- local memory size；
- ISA flags；
- memory bank count/size。

部分 caps 不编码在 capability word 中，需要 backend 解析：cache line size、global memory size、clock rate、peak memory bandwidth。

runtime design 的重点是：software 应 query visible capabilities，而不是 include private hardware config headers。

## 本地迁移清单

- 先定义 public handles：device、buffer、queue、event、module、kernel。
- 单独定义 backend transport：register read/write、DMA、host memory、simulator callback、RTL bridge。
- 多 kernel launch 前定义 module format 和 kernel entry resolution。
- 定义 argument staging 和 lifetime。
- 定义 grid/block/local memory/entry/args 的 DCR/MMIO launch records。
- 定义 completion、timeout、fence、event、cache flush behavior。
- 至少添加一个 workload，通过 public runtime path 在 simulator 和 RTL-style backend 上运行。

## 不要照搬的内容

- 不要把 internal RTL wires 暴露成 public API。
- 当前 milestone 不需要时，不要引入完整 Vortex CP。
- modules/kernels 存在后，不要在 tests 中 hard-code kernel entry PC。
- 没有 ordering/completion semantics 时，不要添加 async queues/events。
- runtime 不要 include private hardware config header；需要时用 capability query 或 generated ABI header。
