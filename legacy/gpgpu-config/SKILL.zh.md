---
name: gpgpu-config
description: 用于验证 GPGPU config defaults、hardware-private fields、simulator-private fields、ABI-visible constants、test-only fields 或 debug-only fields 是否绑定到 SPEC_IR 和 GPU_STATE_IR。
---

# GPGPU Config Binding Validator

## Skill Role

本 skill 是 config ownership 和 binding validation pass。

```text
SPEC_IR.config_defaults + GPU_STATE_IR + CONFIG_BINDING_IR -> config_report
```

它验证 config，不生成架构默认值。

## Input IR

必须输入：

- `SPEC_IR.config_defaults`
- `GPU_STATE_IR`
- `CONFIG_BINDING_IR`
- ABI fields 存在时的 runtime contract

## Output IR

输出：

```text
config_report = {
  config_hash,
  hardware_private,
  simulator_private,
  hw_sw_abi,
  test_only,
  debug_only,
  binding_results,
  ownership_violations,
  verdict
}
```

## Allowed Transformations

- 把 config fields 分类到 ownership classes。
- 检查每个 config field 绑定到唯一 `SPEC_IR` 或 `GPU_STATE_IR` 字段。
- 检查 generated artifacts 引用 state hash 和 transform table version。
- 检查 ABI-visible constants 出现在 runtime contract。

## Forbidden Actions

- 不生成 missing defaults。
- 不把 generated config 当 source of truth。
- 不允许 runtime 修改 `hardware_private` fields。
- 不允许 `simulator_private` fields 影响 RTL trace。
- 不允许 `test_only` 或 `debug_only` fields 影响 canonical execution semantics。

## Required Invariants

- `hw_sw_abi` fields 出现在 runtime contract。
- `hardware_private` fields 不受 runtime 控制。
- `simulator_private` fields 不改变 hardware semantics。
- `test_only` 和 `debug_only` fields 排除在 `GPU_STATE_IR` execution semantics 外。
- 每个 config enum 已由 `gpgpu-spec-lock` resolve。

## Failure Modes

以下情况 reject：

- ABI-visible constant 只存在 RTL。
- config field 有多个 owner。
- debug/test field 影响 execution state。
- simulator-only config 改变 RTL trace。
- default 无法追溯到 `SPEC_IR`。

## Report Schema

`config_report.verdict = CONFIG_LOCKED | CONFIG_REJECTED`。

## Downstream Contract

runtime、RTL、simulator 和 tests 只能消费自己声明的 config class。closure 使用 `config_report` 作为 config lock gate 的 evidence。
