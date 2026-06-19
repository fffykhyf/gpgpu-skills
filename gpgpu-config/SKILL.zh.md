---
name: gpgpu-config
description: 用于添加、编辑或评审 GPGPU parameters、generated config、hardware-private knobs、simulator-private knobs、HW/SW ABI constants、CSR 或 DCR maps、memory maps、kernel ABI values、device capabilities、backend config drift 或 hard-coded core/SIMT-group/thread/cache values。
---

# GPGPU Config

## 概览

当某个值可能在 RTL、simulator、runtime、kernel、tests 或 PPA scripts 之间漂移时使用本 skill。配置工作不只是把数字换成 macros；它是在判断哪些值是 private implementation knobs、哪些值来自 typed parameters、哪些值由协议协商、哪些值是 visible contracts。使用 Rocket Chip 作为 named config fragments、derived parameters、`require` 风格 legality checks 和 resource/capability generation 的参考。使用 XiangShan 作为大型 typed parameter surface、derived backend/cache/memory widths、config-time checks 和 printed/auditable generated microarchitecture 的参考。

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

Generator-visible values 也需要同样纪律。如果某个值控制 topology、address range、source/tag width、cache shape、queue depth、optional feature ports、MMIO layout 或 runtime capability，必须定义 owner，在一个地方派生依赖值，并在 RTL 或 simulator 执行前拒绝非法组合。

## 术语契约

Config 名称使用统一术语；只有引用源码常量时保留参考实现原名。

| 统一术语 | 源码别名 | 配置边界 |
|---|---|---|
| SIMT group | warp、wavefront、wave | execution group width、scheduler residency 和 trace identity |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | ID width、tag fields、trace fields 和 done signals |
| active lane mask | active mask、thread mask、`tmask`、`EXEC` mask | mask width 和 lane-enable ABI |
| CTA/workgroup | CTA、block、workgroup | launch dimensions、group IDs、barriers 和 local memory |
| compute core/CU | core、CU、compute unit | hardware capacity 和 resource allocation |

除非实现已经暴露该名字，否则不要把源码别名写进 public ABI。

对于常见 GPGPU 值族，先按下面方式分类：

| 值族 | 必要分类 |
|---|---|
| SIMT-group and mask sizes | SIMT-group width、active-mask width、physical SIMD width、test thread count 或 FPGA prototype limit |
| SGPR/VGPR/LDS/GDS counts | physical resource、dispatch allocation unit 或 test fixture value |
| dispatcher fields | HW/SW ABI、resource-private 或 debug-only |
| MMIO/control offsets | HW/SW ABI，需要同步 RTL decode、host header、tests、docs |
| unit-test config format | 带 parser validation 的 test ABI |
| conditional build flags | interface-changing、implementation-only、debug-only 或 FPGA-only |

## GPGPU-Sim 配置模式

使用 GPGPU-Sim 作为按 owner 分组配置的参考：

| 分组 | GPGPU-Sim anchor | 本地规则 |
|---|---|---|
| functional/runtime | `-gpgpu_ptx_sim_mode`、stack/heap/sync/pending-launch limits、launch latency | 判断该值是 simulator-private、runtime ABI 还是 device capability。 |
| shader core | `shader_core_config::reg_options()` | topology、registers、scheduler、issue width、FU counts 和 latencies 要绑定到 simulator/RTL consumers。 |
| memory | `memory_config::reg_options()` | cache、shared memory、L2、memory partitions、address mapping、DRAM timing 和 queues 保持在一个可审计族内。 |
| trace/stat | `Trace`、`-gpgpu_runtime_stat`、`-gpgpu_memlatency_stat` | observability knobs 属于 experiment reproducibility。 |
| power | `power_config::reg_options()`、AccelWattch XML/mode options | 做 energy 声明前记录 power model version、config file 和 calibration status。 |

如果 config 使用 GPGPU-Sim 风格的 cache 或 DRAM compact encoded strings，必须提供 parser validation 和 readable expanded dump。

## Rocket Chip 配置模式

使用 Rocket Chip 作为 generator-owned configuration 的参考：

| 模式 | Rocket Chip anchor | 本地规则 |
|---|---|---|
| named fragments | `Configs.scala`、`WithNBigCores`、`WithNMemoryChannels`、`WithRoccExample` | 优先使用小型可组合 config fragments，而不是复制完整大配置。 |
| typed parameters | `RocketCoreParams`、`RocketTileParams`、`DCacheParams`、`L1CacheParams` | 将相关值放入 typed structs 或 schemas，而不是散落常量。 |
| derived values | cache/tag/row/beat/xLen-derived fields | 从源值集中派生 widths、masks、source IDs 和 queue indexes。 |
| legality checks | cache 和 tile parameter code 中的 `require` | 对非法 SIMT-group width、cacheline、bank、MSHR、queue、memory-map 或 ABI 组合早失败。 |
| negotiated protocols | Diplomacy nodes、`TransferSizes`、`AddressSet`、`IdRange` | 将 bus widths、address ranges、transfer sizes 和 IDs 视为 protocol contracts，而不是偶然常量。 |
| generated resources | DTS/resource binding、boot/debug/periphery config | public hardware feature 变化时，同步 capability/version/resource output。 |

## XiangShan Derived-Parameter 模式

使用 XiangShan 作为保持宽配置面可审计的参考：

| 模式 | XiangShan anchor | 本地规则 |
|---|---|---|
| named configs | `top/Configs.scala`、`BaseConfig`、`MinimalConfig` | 保持 target、minimal 和 experiment configs 有名称且可复现。 |
| typed core params | `Parameters.scala` 中的 `XSCoreParameters` | 将 ISA feature flags、widths、queue sizes、memory settings 和 optional units 放在一个 typed surface。 |
| derived backend ports | `BackendParams.scala` | 从 execution-unit configs 派生 issue、wakeup、read/write port、writeback 和 dispatch counts。 |
| cache/MMU params | `DCacheParameters`、TLB/L2TLB params | 从源值派生 tag/index/source widths、ECC bits、MSHR IDs 和 cache-control ranges。 |
| legality checks | `require`、`configChecks` | 当 queue、bank、port、power-of-two 或 ID-range 组合非法时，在 generation 前失败。 |
| auditable output | backend config prints、perf parameter wiring | 当生成 topology 和 derived counts 影响实验或 debug 时，输出可读 dump。 |

本地 GPGPU 工作中，新增 public knob 前先添加 derived-value owner。如果参数会影响 active lane mask width、source/tag width、queue capacity、register file ports、cache shape、runtime capabilities 或 PPA labels，就需要 legality check 和 expanded dump。

## 变更检查表

每个 config 变更都要：

- 说明参数类别。
- 找出 single source of truth。
- 列出 generated 或 synchronized consumers。
- 审计 Verilog `define`、Verilog parameter、C `#define`、scripts、unit-test config、FPGA scripts、generated headers 和 docs 中的重复出现。
- 说明 public capability、version 或 query output 是否变化。
- 移除重复 hard-coded copies。
- 集中派生 active-mask width、source/tag width、cacheline/beat masks、queue index bits 和 memory-map ranges。
- 为最小/最大值和不支持的组合加入 legality checks。
- 如果 protocol width、address range 或 source ID range 变化，同步更新 monitor、trace schema 和 runtime capability。
- 当该值影响 simulator、runtime、memory hierarchy、trace 或 PPA reports 时，记录 config file path 或 digest。
- 为 compact string parameters 提供 readable expanded view。
- 至少测试一个 small config 和一个 target config。
- 如果该值影响 evaluation，更新 PPA config IDs。

## 边界规则

- Hardware-private knobs 可以调优实现，但不能泄漏到 public runtime headers。
- ABI constants 必须通过 generated headers、documented maps 或 explicit capability queries 对所有 consumers 可见。
- Debug/test knobs 不应变成永久 architecture assumptions。
- Derived values 应从 source values 生成，而不是手动复制。
- 修改 visible config 但不更新 tests 和 capability reporting 是 bug。
- Simulator timing knobs 不应静默变成 RTL 或 runtime-visible contracts。
- Negotiated 或 generated protocol fields 不得在 RTL、simulator 或 runtime code 中重复成手写常量。
- 如果存在 MMIO map，修改任何 offset 前先列出 RTL decode path、host C/C++ constants、tests 和 documentation consumer。
- 如果 unit-test config format 变化，同步更新 parser validation、generators、fixtures 和 trace/regression expectations。
- 如果 conditional build flag 会改变 interface，说明它是 public、FPGA-only、debug-only 还是 test-only。

## Drift Signals

看到以下情况时立即使用本 skill：

- lane、SIMT-group、core/CU、register、cache 或 memory sizes 被复制到多个文件。
- simulator 和 RTL 使用不同 constants。
- runtime 从 build flags 猜测 hardware capability。
- generated parameters 在 elaboration 或 code generation 后又被复制成本地常量。
- bus widths、source IDs、address sets、cacheline sizes 或 queue depths 在 producer、consumer 和 monitor 之间不一致。
- tests 只在一个 hard-coded configuration 下通过。
- PPA results 的 config 无法重建。
- trace、power 或 simulator results 没有记录产生它们的 config file 或 option dump。

## 常见错误

- 把每个数字都当成同一种 macro。
- 混合 microarchitecture knobs 和 software ABI constants。
- 更新 RTL，却让 simulator、runtime 或 tests 保留旧值。
- 修改 memory maps 或 CSR/DCR numbers，却没有 capability 或 version story。
- 修改 parameterized logic 后只跑 default config。
- 把 generated/negotiated values 当作注释，而不是 executable constraints。
- 添加 config fragment 却不说明哪些 tests 和 reports 证明它工作。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 generated config/type sources、ABI-visible values、DCR/capability contracts 和 backend config synchronization。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 global definitions、dispatcher parameters、FPGA MMIO registers、Xilinx SDK offsets、unit-test config files 和 SIAGen workload parameters 中分散的 constants。

若想了解与本 skill 相关的 GPGPU-Sim 背景，请阅读本目录下的 `gpgpusim_local.md`。它说明 option registration、tested config files、runtime/core/memory/power/trace knobs 和 compact string caveats。

若想了解与本 skill 相关的 Rocket Chip 背景，请阅读 `../../ref/skillref/rocket.md`，必要时查看 `../../ref_submodule/rocket-chip/src/main/scala/system/Configs.scala`、`tile/BaseTile.scala`、`tile/RocketTile.scala`、`rocket/HellaCache.scala`、`rocket/RocketCore.scala` 和 `diplomacy/Parameters.scala`。

若想了解与本 skill 相关的 XiangShan 背景，请阅读本目录下的 `xiangshan_local.md`。它说明 `Configs.scala`、`XSCoreParameters`、`BackendParams`、DCache/MMU/L2 parameters、legality checks，以及与 GPGPU config 工作相关的 configuration drift lessons。
