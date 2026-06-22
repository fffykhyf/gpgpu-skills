---
name: gpgpu-canonical-state-engine
description: 用于把 locked GPGPU SPEC_IR 转成 deterministic GPU_STATE、验证 GPU FSM invariants，或 snapshot canonical warp、scheduler、memory、register、execution-unit、launch、CSR state。
---

# GPGPU Canonical State Engine

## Objective

把 `SPEC_IR` 转换成唯一 deterministic GPU finite-state machine。

本 skill 不是 architecture planner。禁止 pipeline orchestration、heuristic design、evaluation logic、mapping inference 或 tradeoff synthesis。唯一职责是：

```text
SPEC_IR -> GPU_STATE
```

## Input Contract

输入必须由 `gpgpu-spec-lock` 锁定：

```text
SPEC_IR = {
  ISA: canonical,
  warp_model: explicit,
  memory_hierarchy: explicit,
  scheduling_policy: explicit,
  config_defaults: resolved
}
```

若存在 implicit defaults、unresolved enums、ambiguous natural language、missing state dimensions 或 mode-dependent behavior，必须拒绝。

## Output Contract

只输出一个 canonical state object：

```text
GPU_STATE = {
  warp_state,
  scheduler_state,
  memory_state,
  register_state,
  execution_units,
  launch_state,
  csr_state
}
```

下游 skill 只能消费 `GPU_STATE`，不能重新解释或修改 schema。

## FSM API

所有推理都必须通过 API：

| API | 行为 |
|---|---|
| `init(spec_ir)` | 创建初始 `GPU_STATE`，所有字段显式填充 |
| `apply(event)` | 通过 rule table 应用一个 external/internal event |
| `transition(rule_id)` | 执行一个 named transition rule，并记录 provenance |
| `validate_invariants()` | 每次 transition 前后拒绝非法 state |
| `snapshot()` | 返回 deterministic、serializable、diffable state snapshot |

禁止在 `GPU_STATE` 外维护 hidden state。

## State Schema

| State | Required fields |
|---|---|
| `warp_state` | warp IDs、PC、active mask、predicate mask、reconvergence stack、lifecycle |
| `scheduler_state` | ready set、blocked set、selected warp、stall reason、policy enum |
| `memory_state` | address spaces、cache lines、outstanding requests、ordering/fence state、bandwidth counters |
| `register_state` | scalar/vector/predicate register files、scoreboard dependencies、writeback ownership |
| `execution_units` | unit type、latency、occupancy、accepted ops、completion events |
| `launch_state` | kernel image ID、entry PC、grid/block shape、arguments、resource allocation |
| `csr_state` | control/status fields、trap/fault state、execution-visible counters |

## Transition Rules

每条 rule 必须 table-driven：

```text
rule_id,
precondition,
input_event,
state_reads,
state_writes,
postcondition,
invariants_checked
```

允许的 event class：launch、fetch/decode/issue/execute/writeback、warp divergence/reconvergence、scheduler select/stall/release、memory request/response/fence/fault、CSR read/write/fault。

没有 rule 的 transition 必须 fail closed，不能推断新 rule。

## Invariants

至少验证：

- 每个 valid warp 只有一个 PC 和 active mask。
- active mask 匹配 `warp_model.width`。
- scheduler state 只引用 valid resident warps。
- scoreboard dependencies 引用存在的 registers 和 owning events。
- 每个 outstanding memory request 有唯一 tag/source 和 response owner。
- launch resources 不超过 resolved config defaults。
- 同一 event sequence 下 CSR/fault state deterministic。

## Verification Gate

同一 `SPEC_IR` 和同一 ordered event list 必须满足：

- `init(spec_ir)` 产生相同 snapshot。
- 每次 `apply(event)` 选择相同 `rule_id`。
- `snapshot()` canonical serialization 后 byte-stable。
- `validate_invariants()` 产生相同 pass/fail 和 failure path。

## Failure Modes

- 用 framework evidence 或 papers 发明 state。
- 在 state engine 内补 implicit defaults。
- 允许 RTL/runtime/memory skill 重新解释 state。
- 把多个 transition rules 合成一个 informal step。
- 输出 prose 而不是 serializable `GPU_STATE`。
