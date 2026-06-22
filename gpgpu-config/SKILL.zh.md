---
name: gpgpu-config
description: 用于新增、修改或评审 GPGPU 参数、generated config、hardware-private knobs、simulator-private knobs、HW/SW ABI constants、CSR/DCR maps、memory maps、kernel ABI values、device capabilities、backend config drift 或硬编码 core/SIMT-group/thread/cache values。
---

# Config Schema Compiler Skill

## 1. Objective

把 architecture intent 和 canonical GPU state 编译成 typed、validated config IR，并生成 simulator、RTL、runtime、test、debug 和 PPA artifacts。

## 2. Input Contract: Architecture Intent

输入必须说明：

- 目标 capability 或 experiment。
- 受影响的 canonical GPU state：PC/SIMT group/mask/register file、memory hierarchy、scoreboard/dependency graph、launch state、pipeline state。
- 哪些值是 public ABI，哪些是 private implementation。
- 目标 backend：golden sim、RTL、runtime、memory model、PPA scripts。
- 来自 reference 或 paper 的 evidence constraints。

从一个孤立数字开始的 config change 必须拒绝，直到说明它控制的 state。

## 3. 固定五问

每个 config field 必须回答：

1. What state exists? 指明 GPU state field 或 generated artifact。
2. Who produces it? 指明 config source、derived rule、generator 或 capability query。
3. Who consumes it? 指明 RTL、simulator、runtime、kernel ABI、test、debug 或 PPA consumer。
4. How does it change? 指明 versioning、derivation、legality、migration rules。
5. How do we verify it? 指明 static check、runtime check、elaboration check 或 trace check。

## 4. Output Contract: Typed Config IR

每个字段必须有且只有一个 primary class：

| Class | Meaning | Examples |
|---|---|---|
| HW-private | 只影响实现 | queue depth、FU latency、cache MSHR count、register-bank count |
| ABI-visible | software/kernel 可见 | memory map、CSR/DCR/MMIO offsets、warp size、max block size、argument alignment |
| simulator-only | 只影响模型或观测 | synthetic latency、oracle verbosity、timing-model mode |
| debug-only | trace/assert/watch/timeout/counter | trace enable、watchdog cycles、checker severity |
| test-only | fixture 和 reduced smoke config | small memory、single-warp mode、fake backend flag |
| PPA-only | experiment label/report binding | benchmark suite ID、activity dump path、power model |

Public config 必须生成同步 artifacts：

```text
config.json -> config.sv + config.h + simulator options + runtime capabilities + PPA config_id
```

## 5. Transformation Rules

Config 是 compiler IR，不是参数列表。dependent values 必须集中派生：

| Source value | Derived values |
|---|---|
| `simt_group_width` | active mask width、lane-valid bits、coalescer lane count、trace mask width、runtime capability |
| resident SIMT groups | simt_group_id width、scheduler table depth、scoreboard rows、outstanding-memory owner width |
| register counts | register address width、scoreboard bitsets、operand read ports、spill/capability limits |
| issue/FU topology | issue packet fields、writeback ports、hazard graph、perf counter groups |
| cache line/beat size | byte-mask width、coalescer segment rules、tag/index bits、memory trace schema |
| memory partitions/source IDs | outstanding table size、request tag width、response demux、monitor ranges |
| MMIO/DCR map | runtime headers、RTL decode、capability version、tests、docs |
| max grid/block/local memory | launch ABI checks、resource allocation、runtime error paths、simulator admission |

Derived value 改变时，producer、所有 consumer 和 verification gate 必须同 patch 更新。

## 6. Consistency Constraints

| Binding | Constraint |
|---|---|
| ISA to config | opcode features、register width、memory spaces、atomics、barriers、mask width 必须匹配 semantics |
| RTL to config | generated widths、queue depths、reset values、source IDs、optional ports 必须匹配 elaborated hardware |
| runtime to config | ABI constants、memory maps、capabilities、queue limits、launch limits 必须匹配 generated headers |
| golden sim to config | oracle 使用与 RTL 相同的 instruction、launch、memory、mask parameters |
| memory path to config | cache/coalescer/MSHR/tag/address-space rules 匹配 request/response schema |
| PPA to config | report `config_id` 能重建 source values、derived topology、backend、workload、feature flags |

非法组合必须在 simulation 或 RTL elaboration 前失败。

## 7. State Evolution Rules

1. 添加 source field：class、owner、default、legal range、description。
2. 添加 derived rules 和 generated artifact bindings。
3. 添加 static validation 和一个 negative validation case。
4. ABI-visible field 改变时 bump runtime/capability version。
5. 给 stale config 或 fixture 写 migration note。
6. 测量行为改变时更新 PPA `config_id` 和 report labels。

Debug-only 或 test-only value 不能变成架构假设。

## 8. Verification Gate

| Gate | Must check |
|---|---|
| static check | schema required fields、type/range、power-of-two、cross-field legality、derived values |
| runtime check | capability query、ABI constants、memory map、launch limits、queue limits、version compatibility |
| RTL elaboration check | generated parameter widths、interface fields、optional ports、monitors/assertions |
| simulator check | option dump、canonical trace schema、oracle config digest |
| integration check | small config 和 target config 都能生成匹配 artifacts |
| PPA check | config digest/report path 随 counters 和 workload metadata 保存 |

## 9. Artifact Output

- `config.json`: canonical source 和 derived values。
- `config.sv`: RTL parameters、typedefs、widths、assertions。
- `config.h`: runtime/kernel ABI constants 和 capability version。
- simulator option dump: oracle/timing mode 和 config digest。
- IDs、masks、memory 或 pipeline fields 改变时更新 trace schema。
- static/runtime/elaboration gates 的 validation log。

## 10. Design Evidence Layer

| Evidence | Use |
|---|---|
| GPGPU-Sim | runtime/core/memory/power options 和 compact descriptor 风险的 behavioral evidence |
| Rocket Chip | typed params、fragments、derived fields、legality checks、generated resources 的 structural reference |
| Vortex/MIAOW | GPU-facing ABI constants、DCR/MMIO maps、dispatch fields、test configs 的 implementation anchors |
| XiangShan | large typed parameter surfaces、generated backend/cache widths、audit dumps 的 tradeoff justification |
| CUDA/PTX | warp size、memory spaces、kernel args、sync、capability reporting 的 ABI constraint |

不要添加 framework-pattern headings；把 framework facts 转成 validation constraints 或 evidence notes。

## 11. Failure Modes

- public value 同时出现在 RTL/runtime，却没有 single generated source。
- warp/mask/register/cache width 在 tests/scripts 里手工复制。
- simulator-only timing knob 静默变成 runtime-visible behavior。
- config fragment 改 topology 却不更新 trace schema 和 PPA config ID。
- ABI-visible memory map 改变却没有 version/capability checks。
- illegal parameter combination 进入 RTL elaboration 后才失败。
