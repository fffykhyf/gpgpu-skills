---
name: gpgpu-deterministic-transform-engine
description: 用于通过 fixed table-driven transforms 把 canonical GPU_STATE 映射成 downstream RTL、simulator behavior、runtime、memory 或 PPA artifacts，禁止 heuristic design inference。
---

# GPGPU Deterministic Transform Engine

## Objective

通过 fixed tables 把 `GPU_STATE` 转换成 downstream artifacts。

```text
GPU_STATE -> RTL_MAPPING | SIM_BEHAVIOR | RUNTIME_CONTRACT | MEMORY_MODEL | PPA_MODEL
```

禁止 LLM inference-based design、heuristic mapping 或 opportunistic architecture choice。

## Input Contract

输入必须包含：

- 来自 `gpgpu-canonical-state-engine` 的 `GPU_STATE`。
- transform target。
- mapping table version。
- mode selection provenance。

拒绝 prose specs 和 partially locked state。

## Output Contract

只输出 target artifacts：

| Target | Output |
|---|---|
| `STATE_TO_RTL` | RTL module map、signal map、fixed FSM mapping、hardware trace schema |
| `STATE_TO_SIM` | simulator state model、event interpreter、semantic trace schema |
| `STATE_TO_RUNTIME` | ABI-visible launch/execution contract |
| `STATE_TO_MEMORY` | memory execution model tables |
| `STATE_TO_PPA` | counter map、bottleneck buckets、estimation inputs |

## Table-Driven Mapping

每个 mapping 必须由 fixed enum tables 驱动：

| GPU_STATE enum | Mapping requirement |
|---|---|
| `warp_sched_type` | 映射到唯一 fixed scheduler implementation |
| `cache_policy` | 映射到唯一 fixed cache behavior table |
| `memory_model` | 映射到唯一 fixed ordering and bandwidth model |
| `issue_policy` | 映射到唯一 fixed issue/scoreboard mapping |
| `exec_unit_type` | 映射到唯一 fixed latency/port/trace mapping |
| `launch_abi_version` | 映射到唯一 fixed runtime layout |

mapping table 缺值时 fail closed，不能合成 implementation。

## Transform API

| API | Behavior |
|---|---|
| `select_target(target)` | 选择一个 downstream artifact target |
| `lookup(enum_value)` | 通过 fixed mapping table resolve enum |
| `emit_artifact()` | 产生 deterministic artifact payload |
| `emit_trace_schema()` | 产生 downstream execution 所需 trace fields |
| `validate_mapping()` | 验证每个 consumed state field 有且只有一个 mapping |

## Verification Gate

- 每个 consumed `GPU_STATE` field 被 mapped 或 explicit unused。
- 每个 mapped enum 只有一个 table entry。
- Outputs 包含 mapping table version 和 `GPU_STATE` snapshot hash。
- repeated runs 产生 byte-stable artifacts。
- prose rationale 不能作为 mapping rule。

## Failure Modes

- 从 natural language 推断 RTL structure。
- 因为“更好”选择 cache 或 scheduler。
- 一个 enum 映射到多个 implementations。
- 直接从 `SPEC_IR` 生成 artifacts，而不是从 `GPU_STATE`。
- 隐藏 unmapped state fields。
