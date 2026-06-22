---
name: gpgpu-spec-lock
description: 用于把 GPGPU spec.md、prose requirements、ISA notes、warp model notes、memory hierarchy notes、scheduling policy text 或 config defaults 转成无歧义 SPEC_IR。
---

# GPGPU Spec Lock

## Objective

把 `spec.md` 转换成结构化、无歧义的 `SPEC_IR`。

```text
spec.md -> SPEC_IR
```

本 skill 稳定输入。它不做 architecture design、不选 heuristic、不推断 missing defaults、不生成 downstream artifacts。

## Input Contract

输入是 human-written spec text 和 optional tables。Prose 只能作为 source material，不能传给下游。

## Output Contract

输出：

```text
SPEC_IR = {
  ISA: canonical,
  warp_model: explicit,
  memory_hierarchy: explicit,
  scheduling_policy: explicit,
  config_defaults: resolved
}
```

每个 enum 必须 resolved。每个 default 必须 explicit。每个 ambiguous sentence 必须改写成字段或 reject。

## Locking Rules

- No implicit defaults。
- No natural language ambiguity。
- No unresolved enums。
- No "implementation-defined" behavior，除非编码为 enum value 并声明 allowed consumers。
- No architecture inference from examples。
- No mode-dependent fields，除非 `gpgpu-mode-controller` 已先选择 mode。

## Required Fields

| Section | Required fields |
|---|---|
| `ISA` | opcode set、operand types、mask behavior、memory ops、barriers、CSR access、illegal behavior |
| `warp_model` | warp width、lane IDs、active mask semantics、divergence model、reconvergence rule |
| `memory_hierarchy` | address spaces、cache policy enum、ordering model、bandwidth limits、atomic/fence semantics |
| `scheduling_policy` | scheduler enum、arbitration rule、stall causes、fairness guarantee |
| `config_defaults` | resolved scalar defaults、enum defaults、limits、derived-value owner |

## Lock API

| API | Behavior |
|---|---|
| `parse(spec_md)` | extract candidate fields，不解决 ambiguity |
| `resolve(field)` | 把一个 candidate 转为 canonical enum/scalar/table value |
| `reject(reason)` | spec 信息不足时 fail closed |
| `emit_spec_ir()` | 所有 required fields locked 后输出 canonical `SPEC_IR` |
| `diff_lock(old_ir, new_ir)` | 报告 deterministic field-level changes |

## Verification Gate

- 所有 required fields 存在。
- 所有 enums 属于 declared enum tables。
- `SPEC_IR` 中没有 free-form prose。
- defaults explicit 且可追溯到 spec text。
- `diff_lock` repeated runs 稳定。

## Failure Modes

- 因为 GPU 常见做法而补 missing value。
- 在 IR 中留下 "TBD"、"default"、"typical"、"maybe" 或 "implementation-defined"。
- 把 spec prose 传给 canonical state engine。
- 不 reject 就解决 conflicting requirements。
