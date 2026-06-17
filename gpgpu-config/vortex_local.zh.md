# GPGPU Config 的 Vortex 本地参考

本文件展开 `gpgpu-config` skill 需要的 Vortex 参考，覆盖 parameter classification、generated headers、HW/SW ABI constants、CSR/DCR maps、memory maps、capability reporting 和 drift checks。

## 这个 skill 应该从 Vortex 学什么

Vortex 把 hardware-private build configuration 和 hardware/software ABI constants 分开：

- `VX_config.toml` 描述 microarchitecture 和 implementation knobs。
- `VX_types.toml` 描述硬件/软件共享值：memory map、CSR/DCR maps、VM format、CTA CSRs、counters、enums。
- `ci/gen_config.py` 从 TOML 生成 Verilog headers、C/C++ headers、C flags。
- `configure` 把 source tree 复制到 build directory，并在 build-local `hw/` 和 `sw/` 生成 headers。
- CI guards 防止 private config 泄漏到 public software layers，也防止 software/simulator/hardware include-boundary drift。

本地关键习惯是：改参数前先分类。每个值都属于 hardware-private、simulator-private、HW/SW ABI、test-only 或 debug-only。把所有数字都当作“宏”会导致 config drift。

## 参考阅读顺序

| Path | 关注点 |
|---|---|
| `ref/skillref/vortex.md` | config/ABI lessons。 |
| `ref_submodule/vortex/docs/designs/build_configuration_system.md` | TOML-driven config flow 和 hardware/software layering。 |
| `ref_submodule/vortex/VX_config.toml` | hardware-private 和 simulator/RTL implementation knobs。 |
| `ref_submodule/vortex/VX_types.toml` | HW/SW ABI constants：memory map、CSR/DCR maps、counters、enums。 |
| `ref_submodule/vortex/ci/gen_config.py` | 生成 Verilog、C/C++、cflags outputs。 |
| `ref_submodule/vortex/configure` | build-tree setup 和 generated header creation。 |
| `ref_submodule/vortex/ci/check_config_boundary.sh` | 防止 software/tests include private `VX_config.h`。 |
| `ref_submodule/vortex/ci/check_sw_sim_boundary.sh` | 保持 install-facing software 和 sim/hw internals 隔离。 |
| `ref_submodule/vortex/sw/runtime/common/caps.h` | 从 CP registers 解码 runtime-visible capability。 |

## `VX_config.toml`：Hardware Build Configuration

`ref_submodule/vortex/VX_config.toml` 是 implementation configuration 参考，包含：

- platform topology：clusters、cores、socket size；
- cache/local-memory enable bits；
- ISA implementation toggles：M/F/D/C/A/V、TCU、DMA/DXA、texture/raster/OM；
- pipeline parameters：warps、threads、barriers、issue width、SIMD width、operand collectors、register-bank counts；
- memory implementation：memory block size、address width、platform banks、platform data size、interleave、peak bandwidth、clock rate；
- LSU knobs：lanes、blocks、line size、input queue size、output queue size；
- FPU/TCU implementation type 和 latency/parallelism knobs；
- cache sizes、ways、replacement policy、writeback、dirty-byte tracking、MSHR sizes、request/response queue sizes、bank counts、memory ports；
- local-memory size 和 bank count；
- VM microarchitecture knobs，例如 TLB size 和 pinned-region size。

这些大多是 hardware-private 或 simulator-private。它们可能影响 public capabilities，但 public software 不应 include generated private config header。需要对软件可见时，用 capability query 或 ABI header。

## `VX_types.toml`：ABI 与 Shared Type Configuration

`ref_submodule/vortex/VX_types.toml` 是 visible contracts 参考，包含：

- global CSR/DCR address widths 和 MPM CSR bases；
- ISA identity constants；
- memory map：user base、stack base/size、local memory base、IO base/end、console buffer layout、exit-code address、page-table base；
- VM page format：page size/log size、address mode (`SV32` 或 `SV39`)、page-table levels、PTE size、page-table size limits；
- DCR maps：base/cache flush/MPM、KMU startup address、kernel entry、args pointer、block/grid dimensions、local memory、block size、warp steps、cluster dimensions，以及 DXA/texture/raster/OM state；
- CSR maps：RISC-V base CSRs、FPU/vector CSRs、GPGPU CSRs、CTA CSRs；
- MPM counter classes 和 core/icache/dcache/l2/l3/memory/TLB/PTW/DXA/TCU/texture/raster/OM counters；
- enums，例如 VM address mode。

这些默认应视为 ABI。改动时检查 RTL、simulator、runtime、kernel startup code、tests、documentation、capability reporting。

## Config Generator

`ref_submodule/vortex/ci/gen_config.py` 是核心 generator。

重要行为：

- 解析有序 TOML 并保留 sections；
- 读取 TOML defaults，并应用 `--cflags` 或 trailing `-D...` overrides；
- 支持 `[[enum]]` 定义 enum-typed parameters；
- 支持 `[[builtin]]`、`[[param]]` 作为 expression-only variables；
- 支持 `expr:` strings 和 backtick expressions，允许 `$NAME` reference；
- lowercase definitions 作为 local/private helper，不输出；
- 可输出 Verilog header (`-f verilog`)、C/C++ header (`-f cpp`)、compiler flags (`-f cflags`)；
- unresolved header mode 便于 preprocessor override；
- resolved mode 用于 fully evaluated constants，尤其是 cflags 和 `VX_types`；
- 对大 hex literal 保留 width，避免 Verilog/synthesis 工具截断地址常量。

本地 config work 应优先使用 generator 或单一结构化源，不要在 RTL、simulator、runtime、tests 中手工复制 derived constants。

## Build Configuration Flow

`ref_submodule/vortex/configure` 展示 configured build tree 的创建方式：

- 读取或默认 `XLEN`、`TOOLDIR`、`OSVERSION`、`PREFIX`；
- 记录 `.config.stamp` signature，使 config 参数变化时 generated files 更新；
- 复制 source subdirectories 并展开 `.in` templates；
- 创建 build-local `hw/` 和 `sw/` output directories；
- 对每个 root TOML 运行 `ci/gen_config.py`；
- Verilog headers 输出到 `<build>/hw/<name>.vh`；
- C/C++ headers 输出到 `<build>/sw/<name>.h`；
- `VX_types` 用 resolved mode，因为 memory-map/VM expressions 依赖 `XLEN`；
- export `XLEN` 供 expression resolution。

generated configuration 应该是 build-local。不要手工编辑 generated headers；改 source TOML 或 override flags。

## Include 与 Layering Boundaries

Vortex 有显式 CI guards。

### `ci/check_config_boundary.sh`

该脚本禁止 software 和 tests include `VX_config.h`。原因是 `VX_config.h` 是 hardware build configuration，只属于 RTL 和 simulator。software 应使用：

- `VX_types.h` 获取 ISA/ABI constants；
- `vx_device_query()` / `VX_CAPS_*` 获取 device properties；
- `config.mk` 获取 build parameters；
- 有意需要 compile-time build config 时使用 generated `-D` flags。

### `ci/check_sw_sim_boundary.sh`

该脚本强制双向隔离：

- `sw/kernel` 和 `sw/runtime` 不能 include 或 reference `hw/`、`sim/` internals；
- `sim/` 和 `hw/` 不能 include install-facing `sw/kernel/include` 或 `sw/runtime/include` headers；
- `sw/common` 是内部 escape hatch。

本地工作也要保留这种边界。如果 runtime 需要硬件事实，要么把它定义为 ABI，要么作为 capability 暴露，要么保持 backend-private。

## Generated Include Points

有用的 Vortex include paths：

- `ref_submodule/vortex/hw/rtl/VX_define.vh`：RTL include point，拉入 generated Verilog config 和 derived macros。
- build-local `hw/VX_config.vh`、`hw/VX_types.vh`：generated RTL headers。
- build-local `sw/VX_config.h`、`sw/VX_types.h`：generated C/C++ headers，其中 `VX_config.h` 对 public layer 仍应视为 private。
- `ref_submodule/vortex/sw/runtime/common/caps.h`：不用 public software include hardware-private config，也能 decode capabilities。

如果 local parameter 通过 public runtime API 可见，优先 generated ABI header 或 capability query。如果只改变硬件结构，保持 hardware-private。

## Runtime Capabilities

`ref_submodule/vortex/sw/runtime/common/caps.h` 解码两个 CP capability words：`GPU_DEV_CAPS` 和 `GPU_ISA_CAPS`。

encoded values 包括：

- version；
- number of threads；
- number of warps；
- number of cores、sockets、clusters；
- issue width；
- local memory size；
- ISA flags；
- number of memory banks；
- memory bank size。

helper 对 backend 必须自行解析的值返回 `false`，例如 cache line size、global memory size、clock rate、peak memory bandwidth。

这是 hardware-private parameter 有 runtime-visible projection 时的好模式：source 保持 private，对外暴露稳定 decoded capability。

## Classification Guide

| Class | Vortex examples | 本地动作 |
|---|---|---|
| hardware-private | MSHR size、queue depth、cache bank count、FU latency | 放 private config；测试 RTL/sim configs。 |
| simulator-private | model-only delay、debug verbosity | 不进入 public ABI。 |
| HW/SW ABI | memory map、CSR/DCR numbers、CTA CSRs、kernel entry、counters | 放 shared generated source；更新所有 consumers。 |
| test-only | tiny smoke-test memory 或 input size | 限于 tests；不要泄漏到 architecture。 |
| debug-only | trace flags、assertions、watchdogs | optional 且 non-semantic。 |

## 本地修改清单

每次 config change 都要：

- 分类参数；
- 找到 single source of truth；
- 列出 generated outputs 和 direct consumers；
- 判断 capability/query output 是否变化；
- 删除 stale hard-coded copies；
- parameterized logic 改动后至少跑一个 small config 和一个 target config；
- evaluation 依赖该值时更新 PPA config id；
- 跑 boundary checks 或等价 grep，确认没有 illegal includes。

## 不要照搬的内容

- 不要无理由复制 Vortex macro names。
- 不要因为 Vortex 中 software 能看到某值，就把所有值移入 ABI。
- 不要只用一个 default config 验证 parameterized RTL。
- 不要手工编辑 generated headers。
- 不要在 public runtime headers 中暴露 private hardware config。
