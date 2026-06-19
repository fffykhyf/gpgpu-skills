---
name: gpgpu-golden-sim
description: 用于设计或调试 GPGPU golden simulator、SimX-like module twin、instruction semantics、trace schema、RTL-vs-simulator comparison、execution mismatch、first divergence 或 regression workflow。
---

# GPGPU Golden Simulator

## 概览

当 simulator behavior、instruction semantics 或 trace comparison 是事实来源时使用本 skill。Simulator 应该是架构的 executable twin，也是 RTL debug 的实用 oracle，而不只是 final-output checker。使用 Rocket Chip 作为补充 ISA 或 timing oracle 的参考：executable protocol monitors、constrained fuzzers、unit-test harnesses 和 trace/resource checks。使用 XiangShan-NEMU 作为 stable reference-model ABI、step-by-step difftest、skip/guided execution、store-commit events、checkpointing 和 first-divergence diagnosis 的参考。

## 核心规则

每个非平凡 RTL 行为在被信任前，都需要 simulator behavior 或 golden trace。对于 bug，在提出硬件修复前先找到 reference 和 implementation 之间的 first divergence。使用能证明当前阶段的最小 oracle：

| 阶段 | Oracle | 使用场景 |
|---|---|---|
| G0 | hand-written expected side effects | 极小 ALU、branch 或 LSU unit tests |
| G1 | external ISA simulator trace | 在完整本地 simulator 出现前扩展指令覆盖 |
| G2 | normalized per-SIMT-group trace | 调试 multi-SIMT-group RTL effects |
| G3 | module-level golden model | scoreboard、LSU、branch 或 barrier ownership 被测试 |
| G4 | cycle-aware simulator | stalls、counters 和 PPA interpretation 依赖 timing |

External functional traces 和 normalized per-SIMT-group RTL traces 适合作为早期 correctness loop，但它们不是 cycle model。

Functional semantics 和 timing behavior 必须保持分离。如果 timing model 或 RTL 与 functional oracle 共享结构，必须显式说明 shared schema：kernel descriptor、instruction metadata、active lane mask、memory access、trace identity 和 config。

并非每个 oracle 都必须是完整 GPU simulator。对于 memory、command queue、MMIO 和 interconnect-like paths，应定义局部可执行契约：request/response legality、source/tag lifetime、address alignment、mask correctness、ordering、replay、fault 和 completion checks。

## 术语契约

Trace schema 和 mismatch report 使用统一术语；只有引用具体 backend 时保留参考实现原名。

| 统一术语 | 源码别名 | Trace 含义 |
|---|---|---|
| SIMT group | warp、wavefront、wave | 带一个 PC 和 active lane mask 的 scheduled execution stream |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | 用来分组 trace events 的稳定 identity |
| active lane mask | active mask、thread mask、`tmask`、`EXEC` mask | 一个事件上的 lane participation state |
| CTA/workgroup | CTA、block、workgroup | launch、barrier 和 local-memory scope |
| compute core/CU | core、CU、compute unit | 拥有 SIMT groups 的 trace source |

## GPGPU-Sim Functional/Timing Split

使用 GPGPU-Sim 作为 oracle 职责分离的参考：

| 层 | GPGPU-Sim anchor | 本地对应 |
|---|---|---|
| Functional semantics | `src/cuda-sim/`、`instructions.cc`、`ptx_thread_info` | ISA oracle 和 architectural state |
| Launch descriptor | `kernel_info_t` | kernel entry、args、grid/block、stream/queue、CTA progress |
| Dynamic instruction event | `warp_inst_t` | 带 SIMT group、PC、active lane mask、operands 和 memory metadata 的 issued instruction |
| Divergence state | `simt_stack` | active-mask 和 reconvergence oracle |
| Timing model | `shader_core_ctx`、`scheduler_unit`、`ldst_unit` | 带 stalls 和 backpressure 的 cycle model 或 RTL trace |
| Trace/debug | `Trace`、stats、component logs | normalized first-divergence artifacts |

在 architecture contract 说明 oracle 错误之前，不要为了匹配 timing artifact 而修改 functional oracle。

## Rocket Chip Checker 模式

使用 Rocket Chip 作为 protocols 和 harnesses 周围局部 oracle 的参考：

| Checker 类型 | Rocket Chip anchor | 本地规则 |
|---|---|---|
| protocol monitor | `tilelink/Monitor.scala` | 将 memory/control protocol rules 写成 assertions，而不是 prose。 |
| constrained fuzzer | `tilelink/Fuzzer.scala` | 生成 legal randomized traffic，并维护 source/tag allocation 和 in-flight tracking。 |
| harness oracle | `system/TestHarness.scala`、`unittest/UnitTest.scala` | 每个 hardware smoke test 都要有 start、finish、timeout、memory/debug 和 success semantics。 |
| trace sink | `trace/` | 为 command、issue、memory、completion 和 fault paths 输出稳定 trace records。 |
| generated docs | docs `mdoc` flow | 让 reference docs 和 code examples 足够接近，方便发现 drift。 |

在完整 golden simulator 下方使用这些 checker。Protocol monitor 可以在 final kernel output 不同之前就抓到错误 lane mask 或 source ID。

## XiangShan-NEMU Difftest 模式

使用 XiangShan-NEMU 作为把 golden model 变成调试接口的参考：

| Difftest 契约 | XiangShan-NEMU anchor | 本地 golden-sim 规则 |
|---|---|---|
| reference ABI | `src/cpu/difftest/ref.c` | 导出稳定的 init、memory copy、state copy、execute、status、interrupt 和 event-copy calls。 |
| DUT adapter | `src/cpu/difftest/dut.c` | 通过稳定接口加载 reference model，并隔离 DUT-specific skip logic。 |
| step compare | `difftest_step(pc, npc)` | 在 final kernel output 之前的中间事件边界进行比较。 |
| state sync | `difftest_regcpy`、`difftest_csrcpy`、uarch status sync | 定义哪些 architectural、control、SIMT 和 memory state 可以 copy 或 query。 |
| non-identical phases | skip-ref、skip-dut、guided exec | 将合法 mismatch windows 显式化，而不是忽略 failures。 |
| long workload support | `src/checkpoint/`、SimPoint workflow | 对长 kernel 和 full-system tests 使用 checkpoints 或 sampled regions。 |

对于 GPGPU 工作，将 register/CSR copy 翻译成 kernel launch state、SIMT group PC、active lane mask、registers、predicate state、barrier state、shared/global memory、memory commit、fault 和 replay events。Final output comparison 只是 smoke test，不是完整 oracle。

## Module Twin Map

对每个新 RTL block，说明 simulator 是否有对应 owner：

| 硬件概念 | 需要定义的 simulator owner |
|---|---|
| SIMT-group scheduler、PC、masks、barriers | scheduler 或 SIMT-group state model |
| decode 和 instruction expansion | decoder 和 sequencer |
| scoreboard 和 hazards | scoreboard model |
| register read/writeback | operand 或 register-file model |
| ALU/FPU/SFU/LSU/TCU | functional unit model |
| memory hierarchy | LSU、coalescer、cache、memory model |
| launch 和 CTA/workgroup dispatch | runtime/KMU/CTA/workgroup model |

避免使用绕开 timing/module boundary 的中央 interpreter。ISA semantics 应靠近拥有对应行为的单元。

## Trace Contract

有用的 trace record 应包含：

| 类别 | 字段 |
|---|---|
| identity | cycle 或 step、sequence ID 或 UUID、compute core/CU ID、simt_group_id |
| control | launch 或 kernel ID、PC、next PC、opcode、active lane mask、predicate mask |
| operands | source registers、source values、destination register |
| commit | writeback valid、value、exception 或 illegal instruction |
| memory | op、lane mask、address、byte enable、data、tag、response |
| scheduling | scoreboard block、operand block、memory block、barrier block、replay |

如果省略某个字段，说明为什么当前阶段不需要它。

## First-Divergence 工作流

1. 在实现前定义 instruction semantics：inputs、outputs、state changes、illegal cases、mask behavior。
2. 在复杂 RTL 前添加或更新 simulator behavior。
3. 发出能覆盖该行为的最小 golden trace。
4. 用同一 program、config、input memory 和 launch shape 跑 RTL 或第二个 backend。
5. 先 diff ordered architectural effects，再看 timing fields。
6. 运行适用的 local protocol monitors 或 harness assertions，把 legality bugs 和 semantic mismatches 分开。
7. 报告第一个 divergent event，并给出足够复现上下文。
8. 判断是 simulator、RTL、memory path、runtime、config、protocol monitor 还是 test harness 违反了契约。

不要为了匹配 RTL output 而编辑 simulator。先判断哪一边违反了 architecture contract。Trace comparison 还必须：

- 比较前 normalize external traces；不要直接 diff raw simulator logs 和 RTL logs。
- 保持 per-SIMT-group streams 或稳定 identity fields，避免 interleaving 掩盖 first divergence。
- 区分 content differences 和 missing trace/hang conditions。
- 先 trace architectural side effects：register writes、special register writes、memory load/store effects、branch、barrier、waitcnt、retire PC。
- 记录 external oracle version、command、input memory、instruction memory 和 launch/config files。
- 对 memory/control paths，记录 protocol legality state：source/tag allocation、outstanding count、address/mask alignment、replay/nack/fault 和 completion ordering。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 SimX executable twin 和 module-aligned simulator/RTL contracts。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 Multi2Sim trace flow、trace parser、tracemon data structures 和 print functions、trace comparator、regression runner，以及 MIAOW oracle 不能证明什么。

若想了解与本 skill 相关的 GPGPU-Sim 背景，请阅读本目录下的 `gpgpusim_local.md`。它说明 `cuda-sim` functional oracle、timing model、shared `kernel_info_t`/`warp_inst_t` abstractions、trace schema 和 functional-versus-timing caveats。

若想了解与本 skill 相关的 Rocket Chip 背景，请阅读 `../../ref/skillref/rocket.md`，必要时查看 `../../ref_submodule/rocket-chip/src/main/scala/tilelink/Monitor.scala`、`tilelink/Fuzzer.scala`、`unittest/UnitTest.scala`、`system/TestHarness.scala` 和 `trace/`。

若想了解与本 skill 相关的 XiangShan 背景，请阅读本目录下的 `xiangshan_local.md`。它说明 NEMU reference/DUT difftest APIs、step comparison、skip/guided execution、store commit、checkpoint/SimPoint flow，以及如何把这些思想翻译成 GPGPU intermediate-state comparison。

## 常见错误

- 只比较 final memory output，而第一个错误 writeback 早已发生。
- 在 bug 出现后才添加 trace fields，而不是早期定义 minimal trace contract。
- 在一个不清楚的 trace 中混合 functional correctness 和 timing fidelity。
- Simulator 结构与 RTL 无关，导致 trace diffs 很难映射回模块。
- 让 timing-model convenience code 变成 ISA oracle。
- 没有 rerun reproducer 和至少一个 regression 就宣称修复。
- 等到 full-kernel mismatch 才发现错误，而不是让 protocol monitor 在源头抓住 invalid request。
- 使用不遵守合法 source/tag、mask、ordering 和 in-flight rules 的随机流量。
- 只比较 final memory output，而 XiangShan-style difftest boundary 本可以暴露第一个 divergent SIMT、memory、barrier 或 fault event。
