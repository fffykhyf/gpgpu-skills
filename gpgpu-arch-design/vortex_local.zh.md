# `gpgpu-arch-design` 的 Vortex 本地参考

本文件是架构设计 skill 的中文 Vortex 参考。它整理了 Vortex 中对分阶段 GPGPU 架构设计有价值的设计文档和代码实现模式。目的不是照搬 Vortex，而是复用它对边界、状态、配置、runtime 和验证证据的组织方式。

## 应该从 Vortex 学什么

Vortex 的价值在于它把 GPGPU 当作完整系统，而不是孤立 RTL core。它把这些层连在一起：

- 硬件 RTL：`ref_submodule/vortex/hw/rtl/`
- 近似周期级 simulator：`ref_submodule/vortex/sim/simx/`
- runtime 和 backend driver：`ref_submodule/vortex/sw/runtime/`
- device-side kernel ABI：`ref_submodule/vortex/sw/kernel/`
- 测试和 backend runner：`ref_submodule/vortex/tests/`、`ref_submodule/vortex/ci/blackbox.sh`
- 配置和 ABI 源：`ref_submodule/vortex/VX_config.toml`、`ref_submodule/vortex/VX_types.toml`
- PPA 和综合证据：`ref_submodule/vortex/docs/synthesis_analysis.md`、`ref_submodule/vortex/hw/syn/`

架构设计的核心结论是：每个新特性在实现前都要说明 layer impact、state contract、config contract、launch contract 和 verification gate。

## Full-Stack 布局

### 设计文档

`ref_submodule/vortex/README.md` 把 Vortex 定义为 full-stack RISC-V GPGPU，并明确列出 SimX、RTL simulation、FPGA targets 等 backend。重要点是同一个 workload 可以走不同 backend，因此架构工作能在不同保真度上验证。

`ref_submodule/vortex/docs/codebase.md` 展示 ownership 划分：

- `hw/rtl`：core pipeline、cache、memory、FPU、interfaces、libs、tensor core。
- `hw/syn`：FPGA、ASIC、开源综合流程。
- `sw/runtime`：host runtime API 和 backend driver。
- `sw/kernel`：device-side API、startup code、link script。
- `sim`：SimX 和 RTL/AFU simulator。
- `tests`：RISC-V、kernel、regression、OpenCL、runtime、graphics、backend tests。

### 对 skill 的含义

本地架构设计不要止步于 RTL block diagram。要同时问：

- ISA 或 device-visible state 是否改变
- simulator reference behavior 是否改变
- RTL state 和 valid-ready contract 是否改变
- runtime launch/API path 是否改变
- kernel ABI 或 entry 假设是否改变
- shared/private config 是否改变
- 测试和 trace 证据是什么
- counter/PPA 证据是什么

## SIMT 状态与 Core Pipeline

### 设计文档

`ref_submodule/vortex/docs/microarchitecture.md` 定义了 Vortex 的 SIMT 模型：

- thread 是最小执行单元。
- warp 共享 PC，并使用 thread/active mask 控制每个 lane 是否参与。
- `TMC` 修改 thread mask。
- `WSPAWN` 激活多个 warp 并跳转到目标 PC。
- `SPLIT`、`JOIN`、`PRED` 通过 IPDOM state 管理 divergence/reconvergence。
- `BAR` 让 warp 在 barrier 释放前 stall。
- pipeline 是 schedule、fetch、decode、issue、execute、commit。

这就是 `gpgpu-arch-design` 要求显式 state contract 的原因：PC、active mask、warp state、registers、memory、CSR/DCR 和 launch state 都是架构级概念。

### RTL 实现细节

`ref_submodule/vortex/hw/rtl/core/VX_core.sv` 把 core 连接成显式 pipeline/control 边界：

- `VX_scheduler` 拥有 warp scheduling 和 SIMT control state。
- `VX_fetch` 消费 `schedule_if` 并访问 I-cache。
- `VX_decode` 解码 fetched instruction data，并向 scheduler 汇报 unlock 信息。
- `VX_issue` 拥有 per-issue slice、instruction buffer、scoreboard/operand path 和 dispatch。
- `VX_execute` 拥有 ALU/FPU/LSU/SFU/TCU，并暴露 `warp_ctl_if`、`branch_ctl_if` 和 LSU client interfaces。
- `VX_commit` 仲裁结果、产生 writeback，并把 committed warp 回报 scheduler。
- `VX_lsu_scheduler` 和 `VX_mem_unit` 位于 execute 与 memory 之间。
- `VX_dcr_data` 和 DCR flush interface 把 runtime-visible control 连接到 core/cache 行为。

关键模式是架构状态不藏在单个大模块中。pipeline stage 之间通过 typed interfaces 通信，例如 `schedule_if`、`fetch_if`、`decode_if`、`dispatch_if`、`commit_if`、`writeback_if`、`warp_ctl_if`、`branch_ctl_if`。

`ref_submodule/vortex/hw/rtl/core/VX_scheduler.sv` 是 SIMT 架构状态最具体的参考。它保存：

- `active_warps`：哪些 warp live。
- `stalled_warps`：哪些 warp 暂时不能 schedule。
- `thread_masks`：每个 warp 的 active lane mask。
- `warp_pcs`：每个 warp 的 PC。
- `mscratch_r`：每个 warp 的 kernel argument pointer/state。
- `cta_id_per_warp_r`：warp 到 CTA 的映射。
- trap CSRs：`mstatus_r`、`mtvec_r`、`mepc_r`、`mcause_r`、`mtval_r`。
- per-CTA/per-warp context RAM：CTA size、block index、block dim、grid dim、lmem address、cluster size、entry PC。

scheduler 会响应这些事件更新状态：

- 来自 `VX_cta_dispatch` 的 CTA dispatch。
- `WSPAWN`、`TMC`、`SPLIT`、`JOIN`、`BAR`、`wsync`。
- branch resolution、trap、mret。
- schedule fire、decode unlock、commit events。

它把可调度 work 计算为 `active_warps & ~stalled_warps`，再过滤 instruction-buffer full，用 `VX_priority_encoder` 选 warp，然后发出包含 thread mask、PC、warp ID、CTA ID、UUID 的 `schedule_if.data`。本地 scheduler 设计前也应该先写清这类状态契约。

`ref_submodule/vortex/hw/rtl/core/VX_issue.sv` 展示 issue width 的组织方式：按 `wid_to_isw` 拆分 decode traffic，为每个 issue slot 创建 `VX_issue_slice`，按 execution unit 转置 dispatch interface，并把 issued warp ID 回报 scheduler。结论是 issue width 和 warp partitioning 是 config-sensitive contract，不应该散落成常量。

`ref_submodule/vortex/hw/rtl/core/VX_commit.sv` 展示 commit/writeback 边界：按 issue slot 仲裁执行单元结果，用 EOP result 生成 `committed_warp_mask`，用 lane mask 和 byte enable 写回。它还输出 warp ID、CTA ID、PC、thread mask、writeback metadata、data、UUID 等 debug trace 字段。因此本地设计也要让 trace identity 和 writeback 语义可见。

### 对 skill 的含义

架构设计至少要给出这个状态表：

| State | Owner | 必须回答 |
|---|---|---|
| PC | scheduler 或 warp table | 何时自增、branch、trap 或 rewind |
| active mask | scheduler/divergence unit | inactive lane 如何影响 writeback 和 memory |
| warp lifecycle | scheduler | inactive、ready、stalled、barrier、replay、done |
| CTA context | launch/CTA dispatcher/scheduler | grid/block/thread IDs、CTA rank、local memory |
| register state | operand/register file path | read/writeback、hazard、byte enable |
| memory state | LSU/memory path | request tag、response routing、ordering |
| control state | CSR/DCR/runtime | host-visible knob 和 device-visible state |

## Kernel Launch、CTA Dispatch 与 Runtime 边界

### 设计文档

`ref_submodule/vortex/docs/designs/vortex_runtime_api.md` 描述 public runtime API。稳定表面是 handle-based：device、buffer、queue、event、module、kernel。架构层重点是 host software 不直接 poke 任意 RTL internal，而是通过 runtime 和 backend transport。

`ref_submodule/vortex/docs/designs/command_processor_control_plane.md` 描述 command processor。host 在 host memory ring 中构造 command cache line，写 doorbell，CP fetch command。command 包括 memory copy、DCR write/read、launch、fence、event wait/signal、cache flush。launch、sync、DMA、cache maintenance 都成为架构边界的一部分。

`ref_submodule/vortex/docs/designs/kernel_entry_and_dispatch.md` 描述 kernel entry。runtime 加载 module，把 kernel name 解析为 entry PC，stage arguments，并写 startup/entry DCR。device startup code 接收 args pointer，然后跳到选定 entry。

`ref_submodule/vortex/docs/designs/cta_clustering_and_dispatch.md` 描述 KMU 如何发 CTA request，以及 per-core dispatcher 如何映射到 warp 和 local-memory placement。

### Runtime 实现细节

`ref_submodule/vortex/sw/runtime/common/device.cpp` 实现 CP setup 和 command submission：

- `Device::cp_init()` 分配 host-visible command ring、head、completion memory。
- 它写 queue registers，例如 ring base、head address、completion address、ring size、queue enable、global CP enable。
- 它读取 device capability registers 来发现 VM 等 feature，而不是在 runtime 中硬编码。
- `Device::cp_submit_cl_()` 把一个 64-byte command line 写入 ring，推进 tail，在 doorbell 前执行 release fence，写 `Q_TAIL_LO/HI`，然后 poll `Q_SEQNUM` 等待完成。

这就是“不要让 testbench poke 变成 runtime interface”的具体实现。即使本地项目比 Vortex 小，也应该定义 load、args、start、wait、completion 和 result path。

`ref_submodule/vortex/sw/runtime/common/queue.cpp` 实现 launch：

- `Queue::enqueue_launch()` 校验 `vx_launch_info_t`。
- retain `Kernel` handle，保证 module image 和 kernel PC 活到 launch retirement。
- 立即复制 host args blob，再 stage 到 device scratch slot。
- 查询 runtime capability，例如 thread/warp 数。
- 计算 `block_size` 和 warp step。
- 写 KMU DCR：startup PC、kernel entry PC、args address、block dims、grid dims、local memory size、block size、warp steps、cluster dims。
- 通过 `Device::cp_submit_launch()` 提交 `CMD_LAUNCH`，并在 launch retirement 后释放 staged args。

这就是 `SKILL.md` 中 launch contract 的代码依据：program/module、kernel entry、args、grid/block shape、start、wait、done、cleanup 必须一起定义。

### Control-plane RTL 实现细节

`ref_submodule/vortex/hw/rtl/cp/VX_cp_pkg.sv` 定义 command ABI：

- command opcodes：`CMD_MEM_WRITE`、`CMD_MEM_READ`、`CMD_MEM_COPY`、`CMD_DCR_WRITE`、`CMD_DCR_READ`、`CMD_LAUNCH`、`CMD_FENCE`、`CMD_EVENT_SIGNAL`、`CMD_EVENT_WAIT`、`CMD_CACHE_FLUSH`。
- command header：reserved bits、flags、opcode。
- `cmd_t` payload：header、三个 64-bit args、optional profile slot。
- per-queue state：ring base、ring mask、head/completion addresses、tail、head、seqnum、priority、enable、profile flag。

`ref_submodule/vortex/hw/rtl/cp/VX_cp_core.sv` 集成 command processor：

- `VX_cp_axil_regfile` 是 host-visible AXI-Lite control register block。
- 每个 queue 有一组 fetch+engine。
- 四个 resource arbiter 串行化 KMU launch、DMA、DCR、event resource。
- host AXI crossbar 承载 command fetch、completion writes、host-side DMA。
- device AXI crossbar 承载 device-side DMA 和 event traffic。
- GPU-facing interface 把 DCR 和 start/busy handshake 连接到 Vortex。

这说明 Vortex 如何把 host/device control 变成真实硬件边界。小项目可以用更简单 command path，但架构设计仍要命名 launch、DCR/config write、memory movement、completion 和 synchronization 的 owner。

### KMU 与 CTA RTL 实现细节

`ref_submodule/vortex/hw/rtl/VX_kmu.sv` 接收 launch DCR：

- startup PC
- kernel entry PC
- startup args pointer
- grid dimensions
- block dimensions
- local memory size
- block size
- warp steps
- cluster dimensions

它遍历 grid 并一次发一个 CTA request。实现中使用 `group_origin` 和 `intra_offset` 连续遍历 clustered CTA，并预计算 `cluster_size`、aligned local-memory size、cluster span，避免 downstream dispatch 做昂贵乘法。

`ref_submodule/vortex/hw/rtl/core/VX_cta_dispatch.sv` 接收 KMU CTA request 并映射到可用 warp。它维护：

- CTA slot ring state。
- remaining-warps tables。
- local-memory ring allocation。
- `cta_slot_per_warp_r` 反向 lookup，用于 retirement。
- per-dispatch registers：PC、entry、block/grid dimensions、args、local memory、cluster size、thread index、active mask。

它还执行 local-memory admission。cluster start 会保留整个 cluster span，保证 cluster members 连续。这是 launch-time architecture rule 变成硬件状态、scheduler-visible CSR state 和 runtime-visible config 的具体例子。

### 对 skill 的含义

任何涉及 launch 或 work distribution 的架构特性都要说明：

- host-visible launch representation
- device-side state representation
- runtime programming sequence
- simulator representation
- RTL ownership
- 使用真实 launch path 的 test workload

## SimX 作为 Architecture Twin

### 设计文档

`ref_submodule/vortex/docs/designs/simx_simulator_architecture.md` 的核心规则是：SimX 没有中央 `Emulator`。ISA semantics 和 timing behavior 住在类似硬件模块的 simulator object 中。Scheduler、decoder、scoreboard、operands、functional units、LSU、coalescer、caches、memory 都有独立 owner。

这对架构设计很重要，因为 simulator 不应该是只检查最终输出的另一个世界，而应该能解释 RTL 和 reference behavior 为什么分歧。

### SimX 实现细节

`ref_submodule/vortex/sim/simx/core.cpp` 构造类似 RTL 的 module graph：

- `Scheduler`
- `Decoder`
- optional `Decompressor`
- `Scoreboard`
- 每个 warp 一个 `Sequencer`
- `Operands`
- per-warp instruction buffers
- memory coalescers
- local memory 和 local-memory switch
- LSU memory adapters
- optional MMUs
- ALU/FPU/LSU/SFU/optional TCU dispatchers
- `AluUnit`、`FpuUnit`、`LsuUnit`、`SfuUnit` 等 functional units
- commit arbiters

这不只是软件组织方式。它让架构工作能先在 SimX 原型化，再在类似边界上和 RTL 比较。

`ref_submodule/vortex/sim/simx/scheduler.cpp` mirror scheduler-owned state：

- `warp_t` 保存 thread mask、PC、UUID、mscratch、FCSR、trap CSRs、CTA CSRs。
- `Scheduler::activate_warp()` 把 CTA context 加载到 warp state，设置 PC/tmask/mscratch，清空 IPDOM stack，激活 warp，并清除 stall state。
- `Scheduler::schedule()` 如果有 CTA 就 dispatch 一个 CTA warp，处理 `wspawn`，选择 active non-stalled warp，用 UUID、core ID、warp ID、CTA ID、PC、thread mask 创建 `instr_trace_t`，然后 suspend warp，等待后续 decode/commit/FU 进展。
- `suspend()` 和 `resume()` 操作 next-state stall mask，对齐硬件 registered scheduling behavior。
- `setTmask()` 更新 warp thread mask，并在没有 active lane 时 retire warp/CTA。

这就是 skill 规则的代码基础：每个架构特性都要决定 simulator twin 的 owner，以及哪些 trace 字段能证明行为。

### 对 skill 的含义

复杂 RTL 之前先定义：

- simulator module owner
- 对应 RTL owner
- trace identity fields
- first-divergence comparison plan

架构级最小 trace 应包含 cycle 或 sequence、core、warp、CTA、PC、instruction、active mask、writeback、memory request/response，以及必要时的 stall/replay reason。

## 配置边界

### 设计文档

`ref_submodule/vortex/docs/designs/build_configuration_system.md` 解释 Vortex 的双文件划分：

- `VX_config.toml`：hardware/simulator-private build config，例如 core/warp/thread 数、issue width、cache size、queue depth、extension enable、pipeline latency、debug knob。
- `VX_types.toml`：software-visible ISA/ABI contract，例如 CSR/DCR numbers、memory map、VM page format、CTA CSRs、device-visible constants、performance counter addresses、enums。

设计规则是 private microarchitecture parameter 和 HW/SW ABI constant 不能意外混在一起。

### 实现细节

`ref_submodule/vortex/ci/gen_config.py` 读取 TOML，支持 `expr:`、public uppercase symbol、private lowercase helper、enum、builtin 和多种输出格式：

- Verilog headers
- C/C++ headers
- compiler flags

它可以输出 unresolved preprocessor-friendly definition，也可以输出 resolved constants。这样 RTL、simulator、runtime、tests 能共享 config，而不用手工复制数值。

`ref_submodule/vortex/configure` 驱动生成：

- 把 project files 复制到 build directory
- export `XLEN`
- 生成 `<build>/hw/VX_config.vh` 和 `<build>/sw/VX_config.h`
- 生成 `<build>/hw/VX_types.vh` 和 `<build>/sw/VX_types.h`
- 对 `VX_types` 使用 resolved output

`ref_submodule/vortex/hw/rtl/VX_define.vh` 是 RTL 的 generated config/type macro include point。runtime capability 逻辑在 `ref_submodule/vortex/sw/runtime/common/caps.h`，device initialization 会在 `device.cpp` 中读取 capability registers。

### 对 skill 的含义

本地架构设计中，每个参数都要分类：

- hardware-private：pipeline depth、queue size、MSHR size、issue width
- simulator-private：debug level、model-only timing
- HW/SW ABI：memory map、CSR/DCR numbers、launch arg layout、capability bits
- test-only：小测试尺寸
- debug-only：trace、watchdog、assertion

如果 software 能观察一个值，就要定义它如何生成、查询、测试和版本化。

## 架构级 Memory Path

详细 LSU/cache 工作属于 `gpgpu-memory-path`，但架构设计仍要把 memory 放进 full-stack contract。

`ref_submodule/vortex/docs/designs/lsu_pipeline_design.md` 描述两阶段 LSU：

- frontend：AGU、address classification、byte enables、store-data shifting、fence lock、response formatting
- backend：request queue、index buffer、optional coalescer、batching、out-of-order response demux

`ref_submodule/vortex/docs/cache_subsystem.md` 描述 bank dispatch、response merge、MSHR、memory request mux/demux、flush、deadlock prevention。

`VX_core.sv` 展示架构级 wiring：

- execute 发出 LSU client interface。
- per-block `VX_lsu_scheduler` 仲裁 client 并控制 queue sizing。
- `VX_mem_unit` 拥有 local memory、dcache path、coalescer counters、DCR flush。
- optional `VX_mmu` 位于 dcache/icache path 与 external memory bus 之间。
- barrier 使用 `warp_ctl_if.lsu_sched_drained`，因此 memory drain 成为 warp-control 行为的一部分。
- performance counters 通过 pending-read accumulation 统计 ifetch、load、store 和 latency。

### 对 skill 的含义

架构设计不要只写“add memory”。要说明：

- 这是 scalar blocking LSU、vector lane memory、non-blocking loads、coalescing、cache 还是 VM？
- lane mask、byte enable、tag、response 如何表示？
- 它如何与 scheduler、barrier、runtime cache flush、counters 交互？

## Testing、Debug 与 PPA 证据

### 设计文档

`ref_submodule/vortex/docs/simulation.md` 记录 `blackbox.sh` driver。它能选择 backend、clusters、cores、warps、threads、cache options、debug/perf flags、app、args。架构结论必须绑定 backend/config/workload tuple。

`ref_submodule/vortex/docs/testing.md` 描述如何在 simx 和 rtlsim 下跑 regression/OpenCL tests，以及一个新 regression test 如何包含 host code、kernel code 和 Makefile integration。

`ref_submodule/vortex/docs/debugging.md` 描述 debug logs、VCD traces、`trace_csv.py`、UUID-sorted simx/rtlsim trace diff、SAIF capture。这支撑 first-divergence debugging 和 power analysis。

`ref_submodule/vortex/docs/synthesis_analysis.md` 描述综合和功耗流程。它要求 configuration flags、isolated build prefix、SAIF/VCD activity、utilization reports、timing reports、WNS/Fmax、vectorless versus activity-annotated power。

### 对 skill 的含义

架构 stage 不能因为图看起来合理就算完成。至少需要一种证据：

- simulator smoke test
- RTL trace diff
- runtime launch test
- config matrix smoke test
- counter report
- synthesis/timing/power report

PPA 结论必须绑定：

- baseline
- variant
- workload
- backend
- config
- correctness state
- counters
- report path
- interpretation

## 在 `gpgpu-arch-design` 中如何使用

写或 review 本地 GPGPU 架构设计时，要求输出：

| Section | Required content |
|---|---|
| Objective | 一个 capability 或 hypothesis |
| Layer impact | ISA、simulator、RTL、runtime、kernel ABI、config、tests、PPA |
| State contract | PC、masks、warp state、registers、memory、CSR/DCR、launch |
| Module ownership | simulator owner 和 RTL owner |
| Config contract | private value 与 HW/SW ABI value |
| Launch contract | module/program、entry PC、args、grid/block/CTA、start/done |
| Trace contract | simulator/RTL comparison 需要的字段 |
| Verification gate | 最小 backend/config/workload 证据 |
| Deferrals | 明确不实现的 Vortex-like advanced features |

## 默认不要从 Vortex 引入的内容

除非用户要求或项目目标需要，否则不要把这些作为第一阶段要求：

- 完整 RISC-V compatibility
- OpenCL、HIP、Vulkan、graphics、tensor stack
- full command processor
- FPGA shell integration
- VM/TLB/PTW
- multi-queue async runtime
- cluster-contiguous local-memory placement
- 全量 Vortex performance counters

把 Vortex 当作成熟边界和证据组织方式的参考。复制纪律，不必复制全部功能。
