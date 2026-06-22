---
name: gpgpu-golden-sim
description: 用于设计或调试 GPGPU golden simulator、SimX-like module twin、instruction semantics、trace schema、RTL-vs-simulator comparison、execution mismatch、first divergence 或 regression workflow。
---

# GPGPU Semantic Oracle Engine Skill

## 1. Objective

定义 GPU state transition 的可执行 semantic ground truth，并生成 canonical traces 来暴露 oracle、RTL、runtime 和 memory behavior 的 first divergence。

## 2. Input Contract

输入是 ISA、launch 或 trace intent，必须包含 config digest、R0 launch descriptor、instruction subset、memory spaces、expected oracle granularity 和 target comparison backend。

## 3. ISA Semantic Contract

ISA contract 是 primary。每条 instruction 必须定义：

- input state：PC、active lane mask、predicate state、register operands、memory operands、launch-visible state。
- transformation：per-lane semantics、scalar/vector behavior、mask behavior、exceptions/illegal cases。
- output state：next PC、register writes、predicate/mask updates、memory request/effect、scoreboard-visible completion、trace event。
- unsupported behavior：明确拒绝的 opcode、address space、barrier、atomic 或 sync mode。

不要为了匹配 RTL timing artifact 修改 ISA semantics，除非 architecture contract 证明 oracle 错了。

## 4. Oracle State Model

| State | Producer | Consumer |
|---|---|---|
| PC per SIMT group | launch descriptor、branch/divergence rules | fetch/decode oracle、RTL trace diff |
| active lane mask | launch、predicate execution、divergence/reconvergence | instruction semantics、memory coalescing、trace |
| register file | launch initialization、writeback semantics | subsequent instructions、RTL diff |
| scoreboard/dependency graph | timing-aware issue/completion model | RTL hazard checks、stall attribution |
| memory hierarchy state | memory semantic model、cache/coalescer model | loads/stores/atomics/fences、memory trace |
| launch state | R0 launch ABI descriptor | kernel entry、IDs、args、memory spaces |
| execution pipeline state | optional cycle model | timing trace、PPA counters |

## 5. 固定五问

每个 oracle feature 必须回答：

1. What state exists? 指明 architectural 或 timing state。
2. Who produces it? Launch ABI、decoder、instruction semantic rule、memory model 或 timing model。
3. Who consumes it? Next instruction、RTL diff、memory path、runtime 或 PPA。
4. How does it change? 定义 transition rules、ordering 和 illegal cases。
5. How do we verify it? 指明 unit test、oracle trace、cross-backend diff 或 first-divergence test。

## 6. Transformation Rules: Warp Execution Model

Semantic execution 以 SIMT group event 排序：

```text
fetch PC -> decode -> apply active mask/predicate -> read operands -> execute semantics -> emit effects -> update PC/mask/register/memory state
```

Cycle-aware extension 可以建模 scheduler stalls、scoreboard waits、memory waits 和 backpressure，但 functional semantics 与 timing state 必须在 trace schema 中分离。

## 7. Memory Ordering Model

| Operation | Required contract |
|---|---|
| load | address space、active lanes、byte enables、return value、fault behavior、ordering scope |
| store | lane mask、byte enables、data merge、visibility、fault behavior |
| atomic | serialization scope、return value、mask restrictions、ordering |
| fence/flush | affected address spaces、host/device visibility、cache/coherence state |
| local/shared memory | CTA/workgroup scope，timing-aware 时可建模 bank conflict |
| global memory | ordering、coalescing-neutral semantic result、fault model |

Memory timing detail 属于 timing trace field，不应成为 ISA semantic result，除非它改变 legal architectural behavior。

## 8. Divergence Model

Oracle 必须拥有：

- branch condition per lane。
- active mask split 和 reconvergence target。
- PC stack 或等价 reconvergence state。
- join behavior。
- predicated instruction 的 mask state。
- illegal divergence 或 unsupported control-flow cases。

Divergence trace 必须包含 old PC/mask、branch target/fallthrough、new PC/mask 和 reconvergence metadata。

## 9. State Evolution

Oracle state 从 launch initialization 演化为有序 SIMT events。每个 event 读取 PC/mask/register/memory state，应用 instruction 和 memory semantics，emit trace record，并更新 next PC、mask、register file、memory state 以及 optional timing/dependency state。

## 10. Trace Schema

| Category | Fields |
|---|---|
| identity | step/cycle、sequence ID、kernel ID、compute core/CU ID、simt_group_id |
| control | PC、next PC、opcode、active lane mask、predicate mask、divergence action |
| registers | source regs/values、destination regs/values、predicate/special register writes |
| memory | op、address space、lane addresses、byte masks、data、tag/source、response/fault |
| dependencies | scoreboard set/clear、dependency graph edge、stall reason |
| launch | grid/block IDs、args pointer、local/shared memory base、resource allocation |
| pipeline | fetch/decode/issue/execute/writeback state（cycle-aware 时） |

省略字段时必须说明当前 gate 为什么不需要。

## 11. First-Divergence Detection Engine

1. 用同一 kernel image、config、args、input memory、launch shape 运行 oracle 和 implementation。
2. 先把 trace normalize 成 canonical records。
3. 先比较 architectural effects：PC/mask、register writes、memory effects、barriers、faults。
4. architectural effects 匹配后再比较 timing fields。
5. 报告 first divergent event：producer、consumer、expected state、observed state、suspected contract。
6. 路由到 config、runtime R0/R1、RTL SIMT core、memory path 或 oracle semantics。

Final memory output 只是 smoke test，不是充分 oracle。

## 12. Output Contract: Oracle Output

- instruction trace。
- memory trace。
- SIMT group/warp state trace。
- 控制流存在时的 divergence trace。
- cycle-aware 时的 timing/stall trace。
- config digest、runtime ABI descriptor、input memory digest、reproduce command。

## 13. Verification Gate

| Gate | Required proof |
|---|---|
| instruction gate | side effects、masks、illegal cases 的 unit tests |
| launch gate | oracle 精确消费 R0 descriptor 和 argument bytes |
| trace gate | trace schema 包含当前 RTL/memory diff 所需 fields |
| first-divergence gate | 已知 mismatch 报告 first wrong event，而不是最终 symptom |
| memory gate | loads/stores/atomics/fences 匹配 memory contract |
| regression gate | fix 后 reproducer 和至少一个 non-regression case 通过 |

## 14. Design Evidence Layer

| Evidence | Use |
|---|---|
| GPGPU-Sim | functional/timing split、kernel descriptor、warp instruction trace、divergence 的 behavioral evidence |
| Rocket Chip | executable monitors、constrained fuzzers、harnesses、trace sinks 的 structural reference |
| Vortex/MIAOW | SimX-like module twins、trace parser/comparator loop 的 implementation anchors |
| XiangShan-NEMU | reference ABI、step comparison、skip/guided execution、checkpointing 的 tradeoff evidence |
| CUDA/PTX | instruction semantics、memory spaces、masks、barriers 的 ISA/ABI constraint |

Evidence 用来验证 oracle contracts，不能作为顶层 framework 章节。

## 15. Failure Modes

- oracle 只是 final-output checker，无法定位 first divergence。
- functional semantics 和 timing behavior 共享隐藏 mutable state。
- trace interleaving 缺少稳定 SIMT group identity。
- memory trace 丢失 lane mask、byte enable、address space 或 destination register。
- RTL timing behavior 被复制成 oracle semantics。
- unsupported instruction 用 placeholder behavior 静默执行。
