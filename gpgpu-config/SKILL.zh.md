---
name: gpgpu-config
description: 用于检查 GPGPU config_defaults、ABI-visible constants、generated headers、memory maps、launch limits 或 capability values 是否已在 SPEC_IR 中显式锁定，并一致反映到 GPU_STATE。
---

# GPGPU Config Lock Validator

## Objective

验证 `gpgpu-spec-lock` 已锁定的 config fields。

本 skill 不再是 schema compiler。禁止 derive new config、generate downstream artifacts、choose defaults 或 reinterpret architecture。

```text
input:  SPEC_IR.config_defaults + GPU_STATE
output: config_lock_report
```

## Input Contract

输入必须包含：

- `SPEC_IR.config_defaults`。
- `GPU_STATE` snapshot。
- `gpgpu-deterministic-transform-engine` 生成的 config artifacts。

拒绝 raw parameter lists、prose defaults 或不在 `SPEC_IR` 中的 values。

## Output Contract

输出：

```text
config_lock_report = {
  locked_fields,
  gpu_state_bindings,
  generated_artifact_bindings,
  missing_or_drifted_fields,
  verdict
}
```

## Validation Rules

| Check | Rule |
|---|---|
| default source | 每个 default 来自 `SPEC_IR.config_defaults` |
| enum source | 每个 enum 已由 `gpgpu-spec-lock` resolve |
| state binding | 每个 config field 映射到唯一 `GPU_STATE` field 或 explicit unused marker |
| artifact binding | generated headers/configs 引用 transform table version 和 state hash |
| ABI binding | ABI-visible constants 匹配 runtime-visible `GPU_STATE.launch_state` 或 `csr_state` |

## Forbidden Behavior

- 创建 config defaults。
- derive hidden values。
- 直接生成 `config.json`、`config.sv` 或 `config.h`。
- 为 config convenience 修改 architecture。
- 把 test-only values 当作 canonical state。

## Verification Gate

- 没有只存在于 generated artifacts 的 config field。
- downstream artifact 不改变 locked value。
- missing values 路由回 `gpgpu-spec-lock`。
- mapping gaps 路由到 `gpgpu-deterministic-transform-engine`。

## Failure Modes

- 因为 previous GPUs 常用而补 missing defaults。
- 让 runtime 或 RTL 定义未锁定在 `SPEC_IR` 中的 value。
- 把 generated config 当 source of truth。
- 用相似名字掩盖 drift。
