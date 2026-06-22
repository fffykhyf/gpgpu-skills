---
name: gpgpu-architecture-synthesizer
description: 用于把 DESIGN_INTENT_IR 通过固定模板、约束表、enum 表和 provenance 转成受限 GPGPU 架构候选。
---

# GPGPU Architecture Synthesizer

## Skill Role

本 skill 是 DESIGN 模式的受限 synthesis pass。

```text
DESIGN_INTENT_IR -> ARCH_CANDIDATE_IR + synthesized_spec_draft
```

它只创建候选，不创建最终 truth。

## Input IR

必须输入：

- `DESIGN_INTENT_IR`
- architecture preset library
- hard constraint table
- quality target table
- enum table

## Output IR

输出：

```text
ARCH_CANDIDATE_IR = {
  candidate_id,
  ARCH_IR,
  synthesized_spec_draft,
  constraint_proof,
  requirement_coverage_matrix,
  quality_estimate,
  rejected_alternatives,
  unresolved_risks
}
```

## Allowed Transformations

### Stage 1: Requirement Coverage

把每个设计 requirement 映射到 architecture owner 或显式 non-goal。

### Stage 2: Template Selection

只能从固定模板选择：

```text
MINIMAL_SIMT_CORE
MULTI_WARP_SINGLE_SM
MULTI_SM_GPGPU
FPGA_SMALL_GPGPU
TENSOR_EXTENDED_GPGPU
```

v2 最小实现可以只支持：

```text
MINIMAL_SIMT_CORE
MULTI_WARP_SINGLE_SM
```

### Stage 3: Parameter Allocation

分配 warp size、max warps per SM、register file size、shared memory size、issue width、scheduler count、LSU depth、cache policy 等字段。

每个参数必须引用：

```text
USER_CONSTRAINT
DESIGN_PRESET
SOLVER_DERIVED
REPAIR_DERIVED
```

### Stage 4: Hard Constraint Checking

quality scoring 之前必须先检查 hard constraints。

### Stage 5: Quality Scoring

只有 hard constraints 通过后才能输出 risk estimate。

## Forbidden Actions

- 不输出 `GPU_STATE_IR`。
- 不绕过 `gpgpu-spec-lock`。
- 不在 template library 外 invent topology。
- 不使用 `COMMON_GPU_DEFAULT`、`MODEL_GUESS` 或 `UNKNOWN` provenance。
- hard constraint 失败后不能继续做 quality scoring。

## Required Invariants

- 每个 intent requirement 都有 owner 或显式 non-goal。
- `warp_size == active_mask_width`，否则 reject。
- `issue_width <= execution_unit_ports`。
- memory request width 不超过 memory interface width。
- ISA operation classes 有 execution-unit owner。
- ABI-visible constants 出现在 `config_contract.hw_sw_abi`。

## Failure Modes

以下情况输出 `REJECTED_ARCH_CANDIDATE`：

- required feature 没有 owner。
- template 不能支持 hard requirement。
- hard constraints 失败。
- 参数缺少允许 provenance。
- synthesized draft 需要推断才能补完整。

## Report Schema

```text
ARCH_SYNTHESIS_REPORT = {
  candidate_id,
  selected_template,
  requirement_coverage_matrix,
  constraint_proof,
  rejected_alternatives,
  quality_estimate,
  unresolved_risks,
  verdict
}
```

`verdict = CANDIDATE_EMITTED | REJECTED_ARCH_CANDIDATE`。

## Downstream Contract

下游只能把 `ARCH_CANDIDATE_IR` 当候选证据。下一个形成 truth 的 pass 是：

```text
synthesized_spec_draft -> gpgpu-spec-lock -> SPEC_IR
```
