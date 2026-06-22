---
name: gpgpu-arch-design
description: 用于规划、分阶段实现或评审 GPGPU 架构，范围包括 ISA、SIMT 执行、模拟器、RTL、runtime 启动、配置、测试、计数器、内存层级、PPA、FPGA bring-up 或路线图决策。
---

# GPGPU Design Orchestrator Skill

## 1. 系统目标

把 architecture intent 编译成一个可验证的 GPU state-machine contract，并保证 config、runtime ABI、semantic oracle、RTL、memory 和 PPA evidence 一致。

## 2. Input Contract

输入是 architecture intent，必须包含 objective、non-goals、target capability、affected GPU state、expected artifacts、evidence constraints 和 known risks。若输入只是 framework name 或 block diagram，先转换成 canonical GPU state。

## 3. Canonical GPU State Model

所有架构知识都必须归一化到以下 state owner：

| State family | 必须包含 |
|---|---|
| compute state | 每个 SIMT group 的 PC、active lane mask、predicate state、scalar/vector register file、special registers、CTA/workgroup IDs |
| memory state | address spaces、shared/global/local memory、cache line state、coalescer state、outstanding request table、memory ordering state |
| launch state | kernel image、entry PC、argument layout、grid/block dimensions、resource allocation、command queue entry、completion/fault state |
| scheduling state | resident SIMT groups、ready/waiting/done lifecycle、scoreboard、dependency graph、barrier state、replay state |
| pipeline state | fetch、decode、issue、execute、memory、writeback、retire/trace、stall/flush reason |
| coherence state | cache ownership/validity、atomic serialization、fence/flush scope、host/device visibility |

不要用 framework 组织设计。GPGPU-Sim、Rocket Chip、Vortex、MIAOW、XiangShan、CUDA/PTX 和论文只能作为 evidence source，用来验证或挑战 canonical state model。

## 3. 固定五问

每个 design artifact 必须回答：

1. What state exists?
2. Who produces it?
3. Who consumes it?
4. How does it change?
5. How do we verify it?

任何答案缺失，都先路由到更窄的 skill，不进入实现。

## 4. Transformation Rules: Mandatory Design Pipeline DAG

```text
Arch -> Config -> Runtime(R0) -> Golden Sim -> RTL -> Memory -> Runtime(R1) -> PPA
```

| Stage | Input contract | Transformation | Output contract | Gate |
|---|---|---|---|---|
| Arch | architecture intent | 归一化成 canonical GPU state | state contract 和 invariants | 五问检查 |
| Config | state contract | 派生 typed config IR 和 generated constants | config.json/config.sv/config.h contract | static legality check |
| Runtime(R0) | config 和 launch intent | 后端前先定义 ABI | launch ABI contract | ABI fixture test |
| Golden Sim | ISA 和 launch ABI | 执行 semantic state transitions | oracle traces | first-divergence readiness |
| RTL | oracle trace 和 config | 实现 pipeline/dependency FSM | execution trace | RTL-vs-oracle diff |
| Memory | issue/memory contract | 实现 memory state machine | memory trace/response contract | hazard/order monitor |
| Runtime(R1) | backend control path | submit/fence/complete/report fault | execution backend contract | host launch smoke |
| PPA | verified variants | 把 evidence 编译成因果 claim | evidence graph and feedback | baseline/variant audit |

## 5. State Evolution

Architecture state 只能通过显式 artifact handoff 演化。每个 pipeline stage 消费上一阶段 output contract，转换 named state，输出新 artifact，并记录允许下一阶段继续的 verification gate。

## 6. Contract Registry

| Contract | 必须包含 | Producer | Consumer |
|---|---|---|---|
| state contract | PC、SIMT lifecycle、mask、register files、scoreboard/dependency graph、memory hierarchy、launch state、pipeline state | orchestrator | all skills |
| config contract | typed parameters、derived values、legality checks、ABI visibility、generated artifacts | `gpgpu-config` | runtime、sim、RTL、memory、PPA |
| launch contract | kernel image、entry PC、args、grid/block shape、resource limits、memory spaces、sync | `gpgpu-runtime` R0 | golden sim、RTL、runtime R1 |
| instruction contract | opcode semantics、operands、mask behavior、side effects、illegal cases、trace fields | `gpgpu-golden-sim` | RTL、memory、PPA |
| memory contract | op、address space、lane mask、byte mask、data、tag/source、ordering、response、fault | `gpgpu-memory-path` | RTL、golden sim、runtime |
| trace contract | identity、cycle/step、PC、mask、instruction、register/memory effect、stall/fault state | golden sim/RTL/memory | PPA、debug |
| evidence contract | baseline、variant、workload、config digest、metrics、counters、causal attribution | `gpgpu-ppa-evaluation` | architecture feedback |

## 7. Cross-Skill Handoff Rules

| From | To | Required artifact |
|---|---|---|
| orchestrator | config | canonical state model 和 visible/private boundary |
| config | runtime R0 | ABI-visible constants、memory map、capability schema |
| config | golden sim/RTL | generated widths、limits、feature flags、trace field schema |
| runtime R0 | golden sim | launch ABI fixture：kernel descriptor 和 argument bytes |
| golden sim | RTL | instruction、warp、register、memory、divergence traces |
| RTL | memory | issue packet 和 memory request/response contract |
| memory | runtime R1 | fence、completion、fault、visibility semantics |
| runtime R1 | PPA | command timeline、launch latency、completion status、workload metadata |
| PPA | orchestrator/config/RTL/memory/runtime | evidence graph 和 controlled feedback target |

## 8. Failure Routing Table

| Failure signal | Route to | First check |
|---|---|---|
| ISA 或 instruction side effect mismatch | `gpgpu-golden-sim` | instruction semantic contract 和 oracle trace |
| PC、active mask、scoreboard、hazard bug | `gpgpu-rtl-simt-core` | SIMT lifecycle 和 dependency graph transition |
| memory ordering、coalescing、tag、cache、fence bug | `gpgpu-memory-path` | memory request/response trace 和 outstanding table |
| launch、argument、queue、event、completion bug | `gpgpu-runtime` | 区分 R0 ABI bug 和 R1 backend execution bug |
| parameter drift 或 generated width mismatch | `gpgpu-config` | source-of-truth 和 derived config rules |
| performance claim 缺因果证据 | `gpgpu-ppa-evaluation` | baseline、variant、workload、counters、attribution |

## 9. Design Invariants

- no deadlocked resident SIMT group，除非 kernel 有意等待未满足的 program condition。
- no illegal memory hazard：每个 request 都有合法 mask、address space、tag/source lifetime、ordering scope 和 response owner。
- scoreboard correctness：dependency 在 issue 前 set，只能由 owner completion release，并在 kill/reset 时按规则 flush。
- launch determinism：相同 kernel image、config、args、input memory、launch shape 产生相同 architectural trace。
- traceability：每个 register/memory side effect 都能追溯到 launch ID、compute core/CU、SIMT group、PC、active mask 和 instruction。

## 10. Design Evidence Layer

Evidence 用来验证 contract，不能作为章节结构。

| Evidence type | Source examples | Allowed use |
|---|---|---|
| behavioral evidence | GPGPU-Sim、Accel-Sim、CUDA/PTX traces | 验证 semantics、launch flow、timing hypothesis、trace fields |
| structural reference | Rocket Chip、Vortex、MIAOW、XiangShan | 支撑 generator discipline、ownership boundary、monitor、counter、handshake |
| ISA/ABI constraint | CUDA、PTX、OpenCL、local kernel ABI | 约束 image format、argument layout、memory spaces、sync |
| empirical justification | papers、benchmark reports、synthesis/PPA reports | 在 baseline/variant control 明确后支撑 tradeoff |
| implementation anchor | local modules、planned files、tests、traces | 把 claim 绑定到可修改/可验证代码 |

本目录的 `gpgpusim_local.md`、`rocket_local.md`、`vortex_local.md`、`miao_local.md`、`xiangshan_local.md` 只能作为 evidence appendix。

## 11. Output Contract

输出必须包含：

- one-sentence objective 和 non-goals。
- canonical GPU state table。
- 每个 state field 的 producer/consumer table。
- design pipeline DAG 的 transformation rules。
- 每个 skill 预期生成的 artifacts。
- verification gates 和 first failure route。
- evidence layer：source、claim、limitation。

## 12. Verification Gate

架构提案离开 orchestrator 前，必须验证它包含六个 contract skeleton sections、固定五问、canonical state mapping、pipeline DAG handoff、failure route，以及只验证 contract 而不定义结构的 evidence layer。

## 13. Failure Modes

- framework 章节替代 canonical state model。
- runtime launch 被当作脚本，而不是 ABI state。
- config values 被复制，而不是 derived/generated。
- simulator trace 只比较最终输出，隐藏 first divergence。
- RTL 把 PC、mask、dependency、memory state 放进一个不可测大块。
- memory request 丢失 SIMT group、lane mask、destination 或 tag identity。
- PPA claim 同时改变多个变量却声称因果结论。
