# GPGPU PPA Evaluation 的 Vortex 本地参考

本文件展开 `gpgpu-ppa-evaluation` skill 需要的 Vortex 参考，覆盖可复现 performance、power、area、timing、counters、workload/config control、SAIF/VCD activity 和 report interpretation。

## 这个 skill 应该从 Vortex 学什么

Vortex 把每个 PPA 结论绑定到 workload、backend、configuration、correctness state、counters、trace/activity file 和 report path。结果不是简单的“更快”或“更小”，而是包含 command、build flags、test input、backend、counter class、synthesis target 和 interpretation boundary。

本地项目要迁移这些习惯：

- baseline 和 variant 只改变一个目标变量；
- 记录 exact config、backend、workload、input size；
- correctness 通过前不要解释性能；
- 用 stall/counter breakdown 解释 speedup；
- 区分 simulator counters、RTL simulation activity、vectorless power、SAIF/VCD-annotated power、post-implementation reports。

## 参考阅读顺序

| Path | 关注点 |
|---|---|
| `ref/skillref/vortex.md` | 从 Vortex 提取出的 PPA discipline。 |
| `ref_submodule/vortex/docs/simulation.md` | backend/app/config/perf/debug 示例和 runtime execution flow。 |
| `ref_submodule/vortex/docs/testing.md` | simx/rtlsim 下的 regression 和 OpenCL/HIP-style tests。 |
| `ref_submodule/vortex/docs/debugging.md` | `--debug`、`--perf`、trace logs、trace CSV、`--saif` capture。 |
| `ref_submodule/vortex/docs/synthesis_analysis.md` | synthesis、timing、area、power、SAIF/VCD、Fmax、utilization、report locations。 |
| `ref_submodule/vortex/VX_types.toml` | core、stalls、memory、cache、TLB/PTW、TCU、graphics、DXA 的 MPM counters。 |
| `ref_submodule/vortex/VX_config.toml` | PPA record 必须捕获的硬件 config variables。 |

## Unified Experiment Runner

`ref_submodule/vortex/ci/blackbox.sh` 是实用 PPA command wrapper。

它接收：

- backend：`--driver=gpu|simx|rtlsim|opae|xrt`
- workload：`--app=<test/app path>`
- architecture config：`--clusters`、`--cores`、`--warps`、`--threads`、`--l2cache`、`--l3cache`
- instrumentation：`--debug`、`--scope`、`--saif`、`--perf`
- trace outputs：`--vcd_file`、`--saif_file`、`--log`
- app arguments：`--args`
- isolated temp build：`--nohup`

内部流程：

- 把 CLI options 转成 `CONFIGS` `-D` flags；
- 选择 runtime backend path；
- 在 `tests/regression`、`graphics`、`mpi`、`opencl`、`hip` 或 direct path 下找 app；
- 用 debug/scope/SAIF/config options build runtime driver；
- export `VORTEX_PROFILING`、`VCD_FILE`、`SAIF_FILE`；
- 运行 `make -C <app> run-<driver>`；
- `--nohup` 时 stage per-invocation app copy，降低 build race。

本地 PPA 应该也有一个可复现 runner，避免散落 shell snippet 丢失 backend/config/workload 记录。

## 需要记录的 Config Axes

`ref_submodule/vortex/VX_config.toml` 包含主要硬件 knob。PPA record 应记录与实验相关的部分：

- topology：clusters、cores、socket size；
- pipeline：warps、threads、issue width、SIMD width、operand collectors、barrier count；
- ISA/features：M/F/D/C/A/V、TCU、DMA/DXA、graphics/texture/raster/OM；
- memory：memory block size、address width、platform banks/data size、peak BW、clock rate；
- LSU：LSU lanes、blocks、line size、input/output queue size；
- cache hierarchy：enable bits、size、ways、writeback、replacement policy、MSHR/request/response queue sizes、bank count、memory ports；
- local memory：log size、bank count；
- VM：TLB size、pinned-region size；
- FPU/TCU implementation type 和 latency knobs。

`ref_submodule/vortex/docs/synthesis_analysis.md` 还记录 `CONFIGS` 示例和 `NUM_CORES` shorthand。结果里优先记录展开后的 flags，方便未来重建 design。

## Performance Counters

`ref_submodule/vortex/VX_types.toml` 定义 MPM counter scheme。常用 counter groups：

- base：cycles、committed instructions；
- scheduler：scheduler idle cycles、active warps、stalled warps、issued warps、issued threads；
- pipeline stalls：fetch、I-buffer、scoreboard、operands、ALU、FPU、LSU、SFU、TCU stalls；
- control flow：branches、divergence；
- instruction mix：ALU、FPU、LSU、SFU、TCU instruction counts；
- core memory：instruction fetches/latency、loads/latency、stores；
- caches：reads、writes、read/write misses、dirty evictions、bank stalls、MSHR stalls；
- memory class：off-chip reads/writes、memory latency、bank stalls、local memory reads/writes/bank stalls、coalescer misses；
- VM/MMU：TLB reads、hits、misses、evictions、PTW walks、PTW latency；
- extension units：TCU、texture、raster、OM、DXA counters。

本地解释规则：IPC 或 runtime change 只是现象。先用 issue、stall、memory、cache、instruction mix counters 解释，再声称 architecture win。

## RTL Counter Sources

`ref_submodule/vortex/hw/rtl/core/VX_core.sv` 是 core-level performance event generation 的来源之一。它把 instruction fetches、loads、stores、pending read latency、scheduler activity、stalls、FU-level activity 等事件接入 MPM counters。

本地 RTL PPA 中，counter 应在 event owner 附近生成：

- scoreboard stalls 靠近 scoreboard；
- operand bank conflicts 靠近 operands/register file；
- LSU queue/cache stalls 靠近 memory；
- scheduler idle/active/issued 靠近 scheduler；
- FU backpressure 靠近 dispatch/FU queues。

不要在 top-level 用猜测方式统计 lower-level unit 为什么 stall，如果该 unit 能直接报告原因。

## SAIF 与 VCD Activity

`ref_submodule/vortex/docs/debugging.md` 和 `ref_submodule/vortex/docs/synthesis_analysis.md` 描述 SAIF capture：

- `rtlsim`、`opaesim`、`xrtsim` 等 RTL driver 可用 `SAIF=1` 构建。
- `blackbox.sh --driver=rtlsim --app=<app> --saif` 会 build SAIF-enabled simulator 并运行 workload。
- `blackbox.sh` 中 `simx` 不支持 SAIF；功耗 activity 必须来自 RTL-capable backend。
- `VCD_FILE` 和 `SAIF_FILE` 环境变量命名 activity outputs。
- `SAIF_INST` 告诉 synthesis tool strip 哪个 simulation hierarchy prefix，使 SAIF signal path 匹配 synthesized netlist。

`ref_submodule/vortex/hw/scripts/saif_filter.py` 可把 master SAIF 切到 DUT subcomponent。它能列 instance hierarchy、按 suffix match 提取 instance path、可选包一层 synthesis top，并保留 nested scope/net names。

activity file 是 workload artifact。不要复用来自不同 config、driver、input size 或 design revision 的 SAIF/VCD。

## Power Analysis Script

`ref_submodule/vortex/hw/scripts/xilinx_power_analysis.tcl` 是 Xilinx power 参考。

它会：

- 从 `DCP_FILE`、`BUILD_DIR` 或 fallback `post_impl.dcp` 找 post-implementation checkpoint；
- 要求 `SAIF_FILE`；
- 可用 `SAIF_INST`，也可从 SAIF hierarchy 和 current Vivado top auto-detect path prefix；
- 写 vectorless baseline report；
- 读 SAIF 并写 `read_saif_mismatch.rpt`；
- 写 `power_saif.rpt`；
- report 前 deassert resets，避免 reset pulse 夸大 steady-state power。

本地 power work 必须说明 power number 是 vectorless 还是 activity-annotated。如果 SAIF mismatch 很多，power result 不是强证据。

## Synthesis 与 Report Locations

`ref_submodule/vortex/docs/synthesis_analysis.md` 记录多个 backend：Xilinx/Vivado、Altera/Quartus、Yosys、Synopsys Design Compiler，也记录 core、cache、memory unit、FPU、TCU、lmem、full Vortex 等 DUT flows。

需要保留的 report：

- utilization：LUT/FF/BRAM/DSP 或 ASIC area cells；
- timing：target period、WNS、critical path、estimated Fmax；
- methodology/DRC；
- clock 和 RAM utilization；
- vectorless power；
- VCD/SAIF-annotated power；
- SAIF annotation mismatch report。

Fmax 的估算可用 `Fmax = 1 / (clock_period - WNS)`。记录 WNS 和 target period，不要只写“timing passed”。

## 本地最小结果记录

每个 PPA result 应包含：

- commit 或 revision；
- baseline command/report path；
- variant command/report path；
- full `CONFIGS` 或 generated config id；
- backend 和 tool versions；
- workload、input size、launch shape、app arguments；
- correctness status 和 known limitations；
- cycles、instructions、IPC、issue utilization；
- stall breakdown；
- load/store/cache/memory counters；
- area/utilization report paths；
- target clock、WNS、estimated Fmax；
- power mode 和 report path；
- interpretation：数据支持什么、不支持什么。

## 不要照搬的内容

- 不要把 Vortex benchmark choices 当作通用证据。
- 不要比较不同 config/workload 后称为 architecture win。
- 不要把 simulator IPC 当作 silicon frequency 或 power。
- 不要只保留 summary numbers 而丢 commands/report paths。
- incorrect design 的 PPA 不可解释。
