---
name: gpgpu-golden-sim
description: 用于设计或调试 GPGPU golden simulator、SimX-like module twin、instruction semantics、trace schema、RTL-vs-simulator comparison、execution mismatch、first divergence 或 regression workflow。
---

# GPGPU Golden Simulator

## 概览

当 simulator behavior、instruction semantics 或 trace comparison 是事实来源时使用本 skill。Simulator 应该是架构的 executable twin，也是 RTL debug 的实用 oracle，而不只是 final-output checker。

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

## 术语契约

Trace schema 和 mismatch report 使用统一术语；只有引用具体 backend 时保留参考实现原名。

| 统一术语 | 源码别名 | Trace 含义 |
|---|---|---|
| SIMT group | warp、wavefront、wave | 带一个 PC 和 active lane mask 的 scheduled execution stream |
| simt_group_id | warp ID、`wfid`、wave ID、wavefront tag | 用来分组 trace events 的稳定 identity |
| active lane mask | active mask、thread mask、`tmask`、`EXEC` mask | 一个事件上的 lane participation state |
| CTA/workgroup | CTA、block、workgroup | launch、barrier 和 local-memory scope |
| compute core/CU | core、CU、compute unit | 拥有 SIMT groups 的 trace source |

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
| control | PC、next PC、opcode、active lane mask、predicate mask |
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
6. 报告第一个 divergent event，并给出足够复现上下文。
7. 判断是 simulator、RTL、memory path、runtime 还是 test harness 违反了契约。

不要为了匹配 RTL output 而编辑 simulator。先判断哪一边违反了 architecture contract。Trace comparison 还必须：

- 比较前 normalize external traces；不要直接 diff raw simulator logs 和 RTL logs。
- 保持 per-SIMT-group streams 或稳定 identity fields，避免 interleaving 掩盖 first divergence。
- 区分 content differences 和 missing trace/hang conditions。
- 先 trace architectural side effects：register writes、special register writes、memory load/store effects、branch、barrier、waitcnt、retire PC。
- 记录 external oracle version、command、input memory、instruction memory 和 launch/config files。

## 本地参考

若想了解与本 skill 相关的 Vortex 背景，请阅读本目录下的 `vortex_local.md`。它说明 SimX executable twin 和 module-aligned simulator/RTL contracts。

若想了解与本 skill 相关的 MIAOW 背景，请阅读本目录下的 `miao_local.md`。它说明 Multi2Sim trace flow、trace parser、tracemon data structures 和 print functions、trace comparator、regression runner，以及 MIAOW oracle 不能证明什么。

## 常见错误

- 只比较 final memory output，而第一个错误 writeback 早已发生。
- 在 bug 出现后才添加 trace fields，而不是早期定义 minimal trace contract。
- 在一个不清楚的 trace 中混合 functional correctness 和 timing fidelity。
- Simulator 结构与 RTL 无关，导致 trace diffs 很难映射回模块。
- 没有 rerun reproducer 和至少一个 regression 就宣称修复。
