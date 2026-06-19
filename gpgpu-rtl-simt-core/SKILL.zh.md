---
name: gpgpu-rtl-simt-core
description: 用于设计、编辑或评审 GPGPU SIMT RTL，包括 SIMT group lifecycle、PC、active masks、IPDOM、split/join、fetch/decode、scheduler、scoreboard、operands、register file、functional units、valid-ready、stall、flush 或 commit 行为。
---

# GPGPU RTL SIMT Core

## 概览

用于 GPGPU 的最小 compute core 工作。保持 SIMT state 明确、模块边界小，并让 RTL 行为能够和 simulator trace 对齐。使用 Rocket Chip 作为 typed parameters、optional unit hooks、ready-valid interfaces、command/response arbitration、local perf events 和 generated tile integration 的参考。不要把 Rocket 的 scalar in-order pipeline 当作 SIMT execution template。

## 核心规则

每个 RTL 变更在编辑逻辑前，都必须先定义 state contract：

- 每个 SIMT group 的 PC。
- Active lane mask 和 predicate 行为。
- SIMT group lifecycle：inactive、ready、issued、waiting、barrier、replay、done。
- 如果控制流变化，说明 IPDOM、split、join、branch 和 reconvergence state。
- Register file read/writeback 和 write conflict 规则。
- Scoreboard set、clear、flush、reset 和 kill 规则。
- Pipeline valid-ready、stall、flush、reset 和 kill 行为。
- Optional feature ownership：decode hook、issue packet fields、ports、config bit、trace field、perf event 和 test gate。
- Protocol boundary：request/response fields、source/tag lifetime、nack/replay/kill priority，以及 LSU 或 control-plane interfaces 的 monitor point。

如果这些规则无法清楚说明，说明模块边界太宽，或架构契约不完整。

## 术语契约

本地设计契约使用统一术语；只有命名 Vortex 或 MIAOW 信号时保留源码别名。

| 统一术语 | 源码别名 | RTL 契约 |
|---|---|---|
| SIMT group | warp、wavefront、wave | 带一个 PC 和 active lane mask 的调度单元 |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | readiness、wait、trace 和 completion tables 的索引 |
| active lane mask | active mask、thread mask、`tmask`、`EXEC` mask | scheduler/divergence/exec logic 拥有的 lane participation state |
| CTA/workgroup | CTA、block、workgroup | 包含 SIMT groups 的 barrier 和 launch context |
| compute core/CU | core、CU、compute unit | resident SIMT groups 和 execution units 的 owner |

## 推荐 Pipeline 边界

| Stage 或 unit | 职责 |
|---|---|
| schedule | 选择 ready SIMT group，暴露 stall reason，跟踪 lifecycle |
| fetch | 按 PC 请求指令并处理 I-cache response |
| decode | 将 instruction bits 转成 control fields |
| issue | 缓冲 decoded instructions、检查 hazards、选择 issue slots |
| operands | 读取寄存器，但不隐藏 hazard owner |
| dispatcher | 将 issue slots 路由到 ALU/FPU/LSU/SFU/TCU |
| execute | 产生 unit results 和 memory requests |
| commit | 应用 writeback、更新 scoreboard、发出 trace |
| integration shell | 暴露 configured ports、debug/perf/trace、runtime-visible status 和 protocol monitor hooks |

避免用一个模块同时完成 schedule、decode、read registers、execute、write back 和 drive memory。

## GPGPU-Sim Translation Rules

使用 GPGPU-Sim 的 shader core 作为 state checklist，而不是 RTL 模板：

| GPGPU-Sim anchor | 需要定义的 RTL owner |
|---|---|
| `shd_warp_t` | resident SIMT-group table：valid、PC、active mask、waiting、outstanding stores、instruction buffer |
| `simt_stack` | branch/divergence/reconvergence state 和 active-mask update rules |
| `scheduler_unit::cycle()` | readiness equation、issue arbitration、stall reason、FU availability |
| `scoreboard` | register dependency set/clear、flush、kill 和 reset behavior |
| `opndcoll_rfu_t` | operand collector、register-bank pressure 和 read-port arbitration |
| `issue_warp()` | 带 SIMT context 和 scoreboard reserve 的 accepted issue packet |
| `writeback()` | destination write、scoreboard release、pipeline count update、trace event |

把每个 C++ queue、vector 和 helper call 翻译成显式 capacity、valid-ready、reset、flush 和 kill behavior。

## Rocket Chip RTL Integration 模式

使用 Rocket Chip 作为集成 optional units 且不模糊 ownership 的参考：

| 模式 | Rocket Chip anchor | 本地 SIMT 规则 |
|---|---|---|
| typed core params | `RocketCoreParams`、`RocketTileParams` | 将 feature flags、widths、counters 和 optional ports 放入 typed config surface。 |
| optional decode hooks | 带 optional M/A/F/D/RoCC/vector features 的 Rocket decode table | 新 uop classes 必须同时声明 decode、issue、scoreboard、writeback、trace 和 test effects。 |
| ready-valid interfaces | `DecoupledIO`、`HellaCacheIO`、RoCC cmd/resp | 明确 backpressure、kill、nack、replay、exception 和 response arbitration。 |
| accelerator command path | `LazyRoCC.scala` command router 和 response arbiter | 将 external 或 optional execution units 视为带 busy、fault、interrupt/status semantics 的 command/response clients。 |
| local events | Rocket event sets 和 cache perf events | 在 scheduler、scoreboard、LSU 和 FU owners 附近添加 perf events。 |

借鉴 integration pattern；不要用 CPU concepts 替代 SIMT scheduler、active-mask、reconvergence、CTA 或 lane semantics。

在实现 issue 或 hazard 逻辑前，state contract 还必须列出拥有 readiness 的 per-SIMT-group tables：

| 表 | 职责 |
|---|---|
| valid entry | decoded instruction residency，以及在 halt、branch、waitcnt、barrier 或 issue 时移除 |
| FU class | resident instruction 的 SALU、SIMD、SIMF、LSU 目标 |
| GPR dependency | SGPR/VGPR source 和 destination readiness |
| SPR dependency | EXEC、VCC、SCC、M0 readiness |
| memory wait | LSU in-flight block，并由 done simt_group_id 释放 |
| branch wait | branch 已发射但未 resolved |
| barrier wait | CTA/workgroup barrier arrival 和 release |
| in-flight limit | maximum outstanding instruction 或 finished-SIMT-group state |

使用显式 readiness equation。具体 LSU issue 条件可以是：

```text
ready = fu_lsu & valid & gpr_spr_ready & ~max_inflight & ~mem_wait & ~branch_wait & ~barrier_wait
```

对于非 LSU 单元，只移除确实不适用的 wait 项。不要把这些 owner 合并成一个无法解释的 `ready`。

## 指令影响检查表

对每类 instruction 或 uop，说明它是否改变：

- PC 或 next PC。
- active lane mask、predicate mask、split/join stack 或 SIMT group status。
- integer、floating、vector 或 predicate registers。
- scoreboard 或 in-flight state。
- memory request、response、fence 或 replay state。
- barrier、CTA、CSR 或 launch-visible state。
- source/tag、byte mask、lane mask、ordering、exception 或 completion status 等 protocol-visible fields。
- perf/debug/trace counters 或 runtime-visible status。

Issue packet 至少应携带 simt_group_id、PC、active lane mask、opcode/FU type、source 和 destination fields、memory metadata、必要时的 scheduler 或 issue slot ID，以及 trace identity。

## Bring-Up 顺序

1. Single SIMT group、single issue、ALU-only、无 divergence。
2. Multi-SIMT-group round-robin scheduler。
3. Register writeback 和 scoreboard。
4. Active mask 和 predicated execution。
5. Branch 加简化 divergence/reconvergence state。
6. 通过 memory-path contract 接入 LSU。
7. Barrier、CTA/workgroup dispatch 和完整 SIMT group lifecycle。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 SIMT state、scheduler/fetch/decode/issue/execute/commit 边界，以及 simulator-aligned RTL contracts。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 CU RTL path、fetch 与 wavepool state、issue readiness equations、scoreboard dependency tables、EXEC/VCC/SCC/M0 ownership、FU writeback 和 trace signals。

若想了解与本 skill 相关的 GPGPU-Sim 背景，请阅读本目录下的 `gpgpusim_local.md`。它说明 `shd_warp_t`、`simt_stack`、scheduler readiness、dynamic `warp_inst_t` issue packets、scoreboard release、operand collection 和 RTL translation caveats。

若想了解与本 skill 相关的 Rocket Chip 背景，请阅读 `../../ref/skillref/rocket.md`，必要时查看 `../../ref_submodule/rocket-chip/src/main/scala/rocket/RocketCore.scala`、`tile/RocketTile.scala`、`tile/BaseTile.scala`、`tile/LazyRoCC.scala` 和 `rocket/HellaCache.scala`。

## 常见错误

- 把 active mask 当成临时信号，而不是 core SIMT state。
- 添加 branch 或 barrier 行为，却没有 reconvergence 或 wakeup 规则。
- 把 hazard 行为隐藏在 operand read logic 里。
- 让 backpressure 依赖无关 always blocks 之间的隐式顺序。
- 复制 GPGPU-Sim C++ timing order，却没有说明 RTL handshakes、table capacity 和 reset/flush behavior。
- 只靠 waveform browsing 调试，而不是对齐 simulator/RTL trace。
- 复制 Rocket 的 scalar core structure，而不是只借鉴它的 config、optional-unit、ready-valid、event 和 integration patterns。
- 添加 optional unit，却没有 decode、scoreboard、trace、perf、config 和 protocol ownership。
