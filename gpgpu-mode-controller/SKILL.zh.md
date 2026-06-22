---
name: gpgpu-mode-controller
description: 用于在 spec locking、state generation、deterministic transformation、execution modeling 或 causal trace analysis 前，选择 GPGPU request 应运行 REPRODUCE 还是 DESIGN mode。
---

# GPGPU Mode Controller

## Objective

只选择一个 mode：

```text
MODE = REPRODUCE | DESIGN
```

这是入口 skill。它禁止参与 state、mapping、design decisions、artifact generation、execution modeling 或 causal analysis。

## Input Contract

输入是 user request 和 available artifacts。除了判断用户想 reproduce 还是 constrained synthesis，不检查 architecture internals。

## Output Contract

输出：

```text
MODE_SELECTION = {
  mode,
  reason,
  next_skill
}
```

`next_skill` 通常是 `gpgpu-spec-lock`。

## Mode Table

| Mode | Use when | Behavior |
|---|---|---|
| `REPRODUCE` | 用户要求匹配 existing spec、trace、paper、config、bug 或 result | strict mapping pipeline；拒绝 creative synthesis |
| `DESIGN` | 用户要求从 constraints 合成新设计 | constrained synthesis pipeline；仍需要 locked enums 和 explicit defaults |

## Forbidden Behavior

- 不修改 `SPEC_IR`。
- 不创建 `GPU_STATE`。
- 不把 state 映射到 RTL、sim、PPA、runtime 或 memory artifacts。
- 不选择 scheduling、cache、memory 或 ISA details。
- 不解决 ambiguous spec language。

## Verification Gate

- Mode 必须是 `REPRODUCE` 或 `DESIGN`。
- Reason 引用 user intent，而不是 architecture preference。
- 不产生 downstream field。
- Ambiguity 路由到 `gpgpu-spec-lock`，不能在这里解决。

## Failure Modes

- 选择 mode 时推断 design details。
- 把 DESIGN 当成 heuristic mapping permission。
- 把 REPRODUCE 当成忽略 missing fields 的 permission。
- 同时返回两个 modes。
