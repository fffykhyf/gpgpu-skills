---
name: gpgpu-rtl-simt-core
description: 用于设计、修改或评审 GPGPU SIMT RTL，包括 SIMT group lifecycle、PC、active masks、IPDOM、split/join、fetch/decode、scheduler、scoreboard、operands、register file、functional units、valid-ready、stall、flush 或 commit behavior。
---

# GPGPU RTL SIMT Execution State Machine Skill

## 1. Objective

把 compute core 实现成 warp/SIMT execution FSM，使 PC、active mask、register、scoreboard、memory 和 pipeline state transitions 都能与 semantic oracle 对齐。

## 2. Input Contract

输入是 RTL execution intent，必须包含 config digest、launch descriptor shape、instruction subset、oracle trace requirement、memory request contract 和 target bring-up gate。

## 3. SIMT State Model

| State | Owner | Consumers |
|---|---|---|
| PC per SIMT group | fetch/divergence unit | instruction fetch、trace、branch update |
| active lane mask | divergence/predicate unit | decode、issue、FU lanes、memory coalescer、trace |
| register file | register/operand unit | operand read、writeback、oracle diff |
| scoreboard/dependency graph | issue/writeback/hazard unit | scheduler readiness、operand read、replay |
| pending memory ops | LSU/memory interface | scheduler wait、response demux、writeback |
| barrier/replay state | CTA/workgroup control、replay owner | scheduler readiness、pipeline kill/reissue |
| pipeline registers | fetch/decode/issue/execute/writeback units | valid-ready、stall、flush、trace |

这些 owner 必须足够分离，使每个 transition 可测、可 trace。

## 4. 固定五问

每个 RTL change 必须回答：

1. What state exists? 指明 SIMT group、mask、register、dependency、memory 或 pipeline state。
2. Who produces it? 指明 RTL unit 和 accepted input event。
3. Who consumes it? 指明 scheduler、FU、LSU、writeback、runtime status、trace 或 PPA counter。
4. How does it change? 定义 reset、issue、stall、completion、replay、flush、kill、done transitions。
5. How do we verify it? 指明 oracle diff、assertion、unit test、trace check 或 regression。

## 5. Transformation Rules: Pipeline FSM

```text
fetch -> decode -> issue -> execute -> writeback
```

| Stage | Input state | Transformation | Output state | Gate |
|---|---|---|---|---|
| fetch | ready SIMT group 和 PC | request instruction，处理 stall/flush | instruction word 和 PC trace | fetch trace matches oracle PC |
| decode | instruction word/config | 生成 uop、operands、FU class、control metadata | decode packet | illegal/unsupported op test |
| issue | decoded packet、mask、scoreboard、FU availability | reserve dependencies 并选择 FU | issue packet | scoreboard set/assertion |
| execute | issue packet | 计算 ALU/FPU/SFU/control 或 memory request | result、branch update、memory op | oracle semantic diff |
| writeback | result 或 memory response | 更新 register file、scoreboard、PC/mask/done | committed trace event | trace diff/dependency release |

每个 valid-ready boundary 必须定义 stall、flush、kill、replay、reset priority。

## 6. Warp Scheduler Policy

Scheduler readiness 必须是 owned state 的显式方程：

```text
ready =
  valid
  & instruction_available
  & active_mask_nonzero
  & scoreboard_sources_ready
  & fu_available
  & ~memory_wait
  & ~barrier_wait
  & ~replay_wait
  & ~done
```

每个 scheduler policy 必须说明 arbitration rule、fairness/deadlock assumption、stall reason priority、branch/barrier/memory/replay 如何 block/release readiness，以及为 PPA 产生的 counters。

## 7. Hazard Rules

| Hazard | Rule |
|---|---|
| RAW | source dependencies clear 后才能 issue，除非明确定义 bypass |
| WAR/WAW | 说明 pipeline 是否 in-order 足以避免，或添加 dependency tracking |
| scoreboard set | accepted issue 前 reserve destination |
| scoreboard clear | 只能由 owning writeback/kill/flush transition clear |
| memory dependency | pending memory op 持有 wait state，直到 response/fault/replay/fence completion |
| divergence | branch 原子更新 PC/mask/reconvergence state 和 trace event |
| replay/kill | replay 必须 preserve 或 reconstruct issue packet/dependency state |
| barrier | CTA/workgroup arrival/release 不能 stranded active SIMT groups |

## 8. Issue Packet Contract

Accepted issue packet 至少携带：

- kernel ID、compute core/CU ID、simt_group_id。
- PC 和 next-PC metadata。
- active lane mask 和 predicate mask。
- opcode、FU class、instruction modifiers。
- source/destination register IDs 和 register class。
- scoreboard reservation metadata。
- memory metadata：op、address-space class、width、lane mask、ordering/fence bits。
- trace identity 和 scheduler/issue-slot ID。
- kill/replay eligibility。

省略字段必须由当前 bring-up stage 解释。

## 9. State Evolution

| Event | State change |
|---|---|
| launch dispatch | allocate SIMT group，初始化 PC/mask/register context，清空 scoreboard/pending memory |
| accepted issue | reserve destination，标记 pipeline/FU busy，emit issue trace |
| ALU writeback | update register file，clear dependency，advance PC，emit commit trace |
| branch/divergence | update PC、active mask、reconvergence state，flush younger invalid work |
| memory issue | allocate pending memory entry，send memory request，block dependent readiness |
| memory response | demux by tag，update registers/fault state，clear pending memory/dependency |
| replay/nack | restore issue eligibility，同时 preserve architectural state |
| barrier arrive/release | update CTA/workgroup barrier state 和 scheduler readiness |
| halt/done | mark SIMT group done，deterministically release resources |
| reset/kill | 按 priority table clear/restore owned state |

## 10. Output Contract: Execution Trace Output

RTL trace 必须包含 fetch/decode/issue/writeback records、PC、active mask、opcode、simt_group_id、scheduler decision、stall reason、scoreboard set/clear、dependency graph events、register writeback、memory issue/response/fault tags、branch/divergence/barrier events、config digest 和 launch descriptor identity。

## 11. Verification Gate

| Gate | Required proof |
|---|---|
| smoke | single SIMT group ALU-only trace matches oracle |
| scheduling | multi-SIMT group policy 和 stall reasons deterministic |
| dependency | RAW/writeback scoreboard tests 通过，包含 negative hazard case |
| mask/divergence | predicated/branch traces match oracle PC/mask transitions |
| memory interface | issue packet 和 memory request trace match memory-path contract |
| reset/flush/kill | priority table asserted and covered |
| trace diff | first-divergence tool 能映射 RTL event 到 oracle event |

## 12. Design Evidence Layer

| Evidence | Use |
|---|---|
| GPGPU-Sim | warp state、SIMT stack、scheduler、scoreboard、issue/writeback traces 的 behavioral evidence |
| Rocket Chip | typed params、optional hooks、ready-valid interfaces、events、integration shells 的 structural reference |
| Vortex/MIAOW | GPU SIMT pipeline boundaries、issue equations、trace signals 的 implementation anchors |
| XiangShan | state ownership、derived issue/writeback ports、recovery、counter placement 的 tradeoff justification |
| golden sim | PC/mask/register/memory side effects 的 semantic evidence |

不要把 CPU rename、ROB、scalar commit 或 framework 章节结构复制进 SIMT design。

## 13. Failure Modes

- active mask 被当成 temporary datapath，而不是 architectural SIMT state。
- scheduler readiness 把所有 dependency causes 折叠成 opaque `ready`。
- scoreboard 由错误 response clear，或在 kill/reset 后残留。
- branch 更新 PC 但没有原子更新 mask/reconvergence state。
- memory tags 不保存 SIMT group、lane mask、destination。
- waveform-only debug 替代 oracle trace diff。
