# GPGPU Skill v2 修改计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` when implementing this plan task by task.

**Goal:** 把当前 v1 的 GPGPU state compiler 从“完整 spec 的确定性复现系统”升级为同时支持“从 0 开始设计”的闭环架构生成系统。

**Architecture:** v2 仍然坚持 `SPEC_IR` 和 `GPU_STATE` 是唯一 truth。新增的 architecture synthesis 只能产生候选架构，候选必须经过 `spec-lock`、`canonical-state-engine` 和 `synthesis-closure-engine` 验收后才能进入下游。

**Tech Stack:** Markdown skills, `SKILL.md` / `SKILL.zh.md`, IR schema documents, deterministic rule tables, trace validation reports.

---

## 1. 当前 v1 的能力边界

当前 `skill/` 已经形成如下主链路：

```text
gpgpu-mode-controller
   ↓
gpgpu-spec-lock
   ↓
gpgpu-canonical-state-engine
   ↓
gpgpu-deterministic-transform-engine
   ↓
runtime / memory / rtl / golden / config validators
   ↓
gpgpu-causal-trace-analyzer
```

这条链路适合处理完整、明确、无歧义的 `spec.md`：

```text
complete spec
 -> SPEC_IR
 -> GPU_STATE
 -> deterministic artifacts
 -> validation reports
```

v1 的正确性来自三条规则：

- `spec-lock` 不补隐式默认值。
- `canonical-state-engine` 是唯一 `GPU_STATE` 生成者。
- `deterministic-transform-engine` 只能 table-driven 地映射下游 artifact。

v1 的缺口是 DESIGN 模式仍然会过早进入 `spec-lock`。当用户只给出“我要设计一个教学用 SIMT GPGPU”这类设计意图时，`spec-lock` 按规则必须拒绝，因为它不能推断 warp size、cache policy、scheduler、ISA 或 memory hierarchy。

## 2. v2 总体结构

v2 需要把入口拆成双路径：

```text
                         ┌────────────────────────────┐
                         │ gpgpu-mode-controller       │
                         └─────────────┬──────────────┘
                                       │
               ┌───────────────────────┴───────────────────────┐
               │                                               │
        REPRODUCE path                                    DESIGN path
               │                                               │
               ↓                                               ↓
        gpgpu-spec-lock                         gpgpu-design-intent-lock
               │                                               │
               │                                               ↓
               │                              gpgpu-architecture-synthesizer
               │                                               │
               │                                               ↓
               │                              gpgpu-synthesis-closure-engine
               │                                               │
               └───────────────────────┬───────────────────────┘
                                       ↓
                       gpgpu-canonical-state-engine
                                       ↓
                    gpgpu-deterministic-transform-engine
                                       ↓
        runtime / memory / rtl / golden / config validators
                                       ↓
                     gpgpu-causal-trace-analyzer
                                       ↓
                         closure accept / refine / reject
```

硬约束：

- `REPRODUCE` 模式不能经过 `gpgpu-architecture-synthesizer`。
- `DESIGN` 模式不能在输入不完整时直接进入 `gpgpu-spec-lock`。
- `gpgpu-architecture-synthesizer` 不能直接输出 `GPU_STATE`。
- `synthesized_spec_draft` 必须由 `gpgpu-spec-lock` 锁成 `SPEC_IR`。
- 下游仍然只能消费 `GPU_STATE`。

## 3. 新增 Skill 1: `gpgpu-design-intent-lock`

### 新增原因

从 0 设计时，用户输入通常是目标和约束，不是完整架构 spec。这个 skill 负责把自然语言设计目标锁成结构化 `DESIGN_INTENT_IR`，避免 synthesizer 直接读取开放式自然语言后自由发挥。

### 建议新增文件

- Create: `skill/gpgpu-design-intent-lock/SKILL.md`
- Create: `skill/gpgpu-design-intent-lock/SKILL.zh.md`
- Create: `skill/gpgpu-design-intent-lock/agents/openai.yaml`

### 输入输出

输入：

```text
user design intent
```

输出：

```text
DESIGN_INTENT_IR = {
  objective,
  non_goals,
  workload_profile,
  target_platform,
  hard_constraints,
  soft_constraints,
  required_features,
  optional_features,
  validation_target,
  prototype_credibility_target
}
```

### 必须写入的规则

- 不输出 `SPEC_IR`。
- 不选择 SM count、warp size、cache policy、scheduler、ISA 或 memory hierarchy。
- 只把用户目标转换为 `DESIGN_INTENT_IR`。
- 当 objective、workload、platform 或 validation target 缺失时，必须拒绝或要求显式 preset。
- 允许使用固定 preset，但 preset 必须是显式 enum，不能临时生成。

### 建议固定 preset

```text
MINIMAL_TEACHING_GPGPU
RESEARCH_SIMT_BASELINE
FPGA_SMALL_GPGPU
RTL_SYNTHESIZABLE_BASELINE
GPGPU_WITH_TENSOR_EXTENSION
```

### 增加的能力

这个 skill 让系统能接受“不完整设计意图”，但不会破坏 `spec-lock` 的无推断原则。它把“用户想要什么”稳定下来，把“架构怎么选”留给后续受限 synthesizer。

## 4. 新增 Skill 2: `gpgpu-architecture-synthesizer`

### 新增原因

v1 没有合法的设计生成器。v2 需要一个受限 synthesizer，但它只能生成候选架构，不能成为 truth source。

### 建议新增文件

- Create: `skill/gpgpu-architecture-synthesizer/SKILL.md`
- Create: `skill/gpgpu-architecture-synthesizer/SKILL.zh.md`
- Create: `skill/gpgpu-architecture-synthesizer/agents/openai.yaml`

### 输入输出

输入：

```text
DESIGN_INTENT_IR
architecture_preset_library
hard_constraint_table
quality_target_table
enum_table
```

输出：

```text
ARCH_CANDIDATE = {
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

### 五阶段内部结构

#### Stage 1: Requirement coverage

生成 `REQUIREMENT_MATRIX`，检查每个 intent 字段是否有架构 owner。

| intent 字段 | 必须映射到 |
|---|---|
| workload_profile | compute / memory ratio |
| target_platform | area / frequency / resource limit |
| required_features | ISA / runtime / memory / RTL modules |
| non_goals | 明确禁止生成的模块 |
| validation_target | 必须生成的测试门槛 |

没有 owner 的 requirement 必须拒绝，不能继续。

#### Stage 2: Architecture template selection

只能从固定模板选择，不能临时 invent topology。

建议 v2 最小先支持：

```text
MINIMAL_SIMT_CORE
MULTI_WARP_SINGLE_SM
```

后续扩展：

```text
MULTI_SM_GPGPU
FPGA_SMALL_GPGPU
TENSOR_EXTENDED_GPGPU
```

每个模板必须声明：

```text
supported_features
unsupported_features
required_config_fields
expected_validation_gates
known_risks
```

#### Stage 3: Parameter allocation

生成架构参数，但每个字段必须带来源：

```text
USER_CONSTRAINT
PRESET_DEFAULT
SOLVER_DERIVED
REPAIR_DERIVED
```

禁止来源：

```text
COMMON_GPU_DEFAULT
MODEL_GUESS
UNKNOWN
```

典型参数包括：

- `warp_size`
- `max_warps_per_sm`
- `register_file_size`
- `shared_memory_size`
- `issue_width`
- `num_schedulers`
- `load_store_queue_depth`
- `l1_cache_policy`
- `l2_cache_policy`

#### Stage 4: Hard constraint checking

硬约束必须先于 quality scoring。

最低约束包括：

- `warp_size == active_mask_width`
- `max_warps_per_sm * registers_per_warp <= register_file_capacity`
- `shared_memory_per_block * resident_blocks <= shared_memory_capacity`
- `issue_width <= execution_unit_ports`
- `memory_request_width <= memory_interface_width`
- `launch block dim <= hardware launch limit`
- ISA op classes 必须有 execution unit owner。
- ABI-visible constants 必须出现在 `config_contract.hw_sw_abi`。

硬约束失败时输出 `REJECTED_ARCH_CANDIDATE`，不能包装成可接受设计。

#### Stage 5: Quality scoring

质量评分只能在 hard pass 后执行。它不是正确性证明，只用于避免“合法但明显不适合目标”的候选通过。

输出：

```text
QUALITY_ESTIMATE = {
  perf_risk,
  area_risk,
  memory_bottleneck_risk,
  rtl_complexity_risk,
  verification_risk,
  overall_score
}
```

### 增加的能力

这个 skill 让系统具备“从设计意图生成候选架构”的能力，但保持候选身份。它不会绕过 `spec-lock`，也不会直接污染 `GPU_STATE`。

## 5. 新增 Skill 3: `gpgpu-synthesis-closure-engine`

### 新增原因

synthesizer 本身不可信。v2 需要一个验收中心来保证错误 candidate 无法通过闭环。

### 建议新增文件

- Create: `skill/gpgpu-synthesis-closure-engine/SKILL.md`
- Create: `skill/gpgpu-synthesis-closure-engine/SKILL.zh.md`
- Create: `skill/gpgpu-synthesis-closure-engine/agents/openai.yaml`

### 输入输出

输入：

```text
ARCH_CANDIDATE
SPEC_IR
GPU_STATE
transform artifacts
runtime / memory / rtl / golden / config reports
```

输出：

```text
SYNTHESIS_ACCEPTANCE_REPORT = {
  candidate_id,
  input_hash,
  spec_ir_hash,
  gpu_state_hash,
  hard_constraint_result,
  requirement_coverage_result,
  state_invariant_result,
  artifact_mapping_result,
  trace_smoke_result,
  quality_gate_result,
  stability_result,
  verdict,
  repair_request
}
```

`verdict` 只能是：

```text
ACCEPT
REJECT
REFINE_REQUIRED
INSUFFICIENT_EVIDENCE
```

### 八个验收 gate

| Gate | 检查内容 | 失败后行为 |
|---|---|---|
| Requirement coverage | intent 中的 objective、constraint、required feature 是否映射到 `ARCH_IR` 或 non-goal | `REJECT` 或 `REFINE_REQUIRED` |
| Spec round-trip | `ARCH_IR -> synthesized_spec_draft -> SPEC_IR` 后核心字段是否漂移 | `REJECT` |
| State invariant | `gpgpu-canonical-state-engine.validate_invariants()` 是否通过 | `REJECT` |
| Artifact mapping | `gpgpu-deterministic-transform-engine.validate_mapping()` 是否覆盖所有 consumed fields | `REJECT` |
| Config lock | config 分类是否正确，ABI-visible 是否进入 runtime contract | `REJECT` |
| Trace smoke | runtime / memory / RTL / sim trace 是否最小对齐 | `REFINE_REQUIRED` 或 `REJECT` |
| Quality gate | 是否满足 `validation_target` 和 `prototype_credibility_target` | `REFINE_REQUIRED` |
| Stability gate | 相同输入是否 byte-stable，小扰动是否局部化 | `INSUFFICIENT_EVIDENCE` 或 `REJECT` |

### 最小 v2 gate 范围

第一版先实现四个 gate：

```text
requirement coverage
spec round-trip
state invariant
artifact mapping
```

后续再加入：

```text
config lock
trace smoke
quality gate
stability gate
```

### 增加的能力

这个 skill 让 DESIGN 模式形成可验收闭环。系统不再依赖 synthesizer “看起来合理”，而是依赖 closure gates 阻止错误设计进入下游。

## 6. 新增 IR Schema

### 建议新增文件

- Create: `skill/references/ir/DESIGN_INTENT_IR.v1.md`
- Create: `skill/references/ir/ARCH_IR.v1.md`
- Create: `skill/references/ir/SYNTHESIS_ACCEPTANCE_REPORT.v1.md`
- Create: `skill/references/ir/FIELD_PROVENANCE.v1.md`

### `DESIGN_INTENT_IR.v1.md`

负责定义从自然语言设计目标锁定后的结构：

```text
DESIGN_INTENT_IR = {
  objective,
  non_goals,
  workload_profile,
  target_platform,
  hard_constraints,
  soft_constraints,
  required_features,
  optional_features,
  validation_target,
  prototype_credibility_target,
  preset
}
```

它保证输入目标稳定，不承载架构事实。

### `ARCH_IR.v1.md`

负责定义候选架构结构：

```text
ARCH_IR = {
  design_identity,
  objective,
  non_goals,
  compute_topology,
  execution_units,
  memory_hierarchy,
  ISA_profile,
  ABI_launch_contract,
  config_contract,
  quality_model,
  provenance
}
```

它不是最终执行状态，只是 candidate design。

### `SYNTHESIS_ACCEPTANCE_REPORT.v1.md`

负责定义 closure 验收结果：

```text
SYNTHESIS_ACCEPTANCE_REPORT = {
  candidate_id,
  input_hash,
  spec_ir_hash,
  gpu_state_hash,
  gate_results,
  verdict,
  repair_request
}
```

它是 DESIGN 模式的最终验收报告。

### `FIELD_PROVENANCE.v1.md`

负责定义字段来源：

```text
FIELD_PROVENANCE = {
  field_name,
  source_kind,
  source_id,
  derivation_rule,
  owner_skill
}
```

允许来源：

```text
USER_CONSTRAINT
DESIGN_PRESET
SOLVER_DERIVED
REPAIR_DERIVED
HUMAN_SPEC
```

禁止来源：

```text
UNKNOWN
COMMON_GPU_DEFAULT
MODEL_GUESS
```

## 7. 修改现有 Skill: `gpgpu-mode-controller`

### 修改文件

- Modify: `skill/gpgpu-mode-controller/SKILL.md`
- Modify: `skill/gpgpu-mode-controller/SKILL.zh.md`

### 当前职责

当前只输出：

```text
MODE_SELECTION = {
  mode,
  reason,
  next_skill
}
```

### v2 修改

输出扩展为：

```text
MODE_SELECTION = {
  mode,
  input_kind,
  reason,
  next_skill,
  forbidden_next_skills
}
```

新增 enum：

```text
input_kind = COMPLETE_SPEC | DESIGN_INTENT | PATCH_REQUEST | TRACE_DEBUG
```

### 新路由规则

| 用户请求类型 | mode | input_kind | next_skill |
|---|---|---|---|
| 复现这个 spec | `REPRODUCE` | `COMPLETE_SPEC` | `gpgpu-spec-lock` |
| 按这个完整 spec 生成设计 | `REPRODUCE` | `COMPLETE_SPEC` | `gpgpu-spec-lock` |
| 从 0 设计一个 GPGPU | `DESIGN` | `DESIGN_INTENT` | `gpgpu-design-intent-lock` |
| 设计一个小型 FPGA GPGPU | `DESIGN` | `DESIGN_INTENT` | `gpgpu-design-intent-lock` |
| 修改 warp size 看影响 | `DESIGN` | `PATCH_REQUEST` | `gpgpu-design-intent-lock` 或 `gpgpu-synthesis-closure-engine` |
| 分析为什么慢 | `REPRODUCE` | `TRACE_DEBUG` | `gpgpu-causal-trace-analyzer` |

### 必须新增禁止规则

```text
In DESIGN mode, do not route directly to gpgpu-spec-lock unless the user has already provided a complete architecture spec.
```

### 增加的能力

mode-controller 能区分“完整 spec 复现”和“从目标出发设计”。这会阻止 DESIGN 请求错误进入 `spec-lock` 并被不必要地拒绝。

## 8. 修改现有 Skill: `gpgpu-spec-lock`

### 修改文件

- Modify: `skill/gpgpu-spec-lock/SKILL.md`
- Modify: `skill/gpgpu-spec-lock/SKILL.zh.md`

### 当前职责

当前是：

```text
spec.md -> SPEC_IR
```

### v2 修改

输入增加来源：

```text
source_kind = HUMAN_SPEC | SYNTHESIZED_SPEC_DRAFT
```

`SPEC_IR` 增加 provenance：

```text
provenance = {
  field_name,
  source_kind,
  source_id,
  derivation_rule,
  owner_skill
}
```

当 `source_kind = SYNTHESIZED_SPEC_DRAFT` 时：

- 每个字段必须有 synthesis provenance。
- 每个生成值必须引用 `USER_CONSTRAINT`、`DESIGN_PRESET`、`SOLVER_DERIVED` 或 `REPAIR_DERIVED`。
- provenance 为 `UNKNOWN` 的字段不能接受。
- synthesized spec draft 必须在不推断的情况下 lock 成 `SPEC_IR`。

### 增加的能力

`spec-lock` 能接受 synthesizer 生成的 draft，但不会因为 draft 看起来完整就放松规则。它把“设计生成的值来自哪里”显式保留下来。

## 9. 修改现有 Skill: `gpgpu-canonical-state-engine`

### 修改文件

- Modify: `skill/gpgpu-canonical-state-engine/SKILL.md`
- Modify: `skill/gpgpu-canonical-state-engine/SKILL.zh.md`

### v2 修改

`GPU_STATE` 增加元信息：

```text
design_identity
source_spec_hash
synthesis_candidate_id
state_schema_version
```

新增 invariant：

- `GPU_STATE` 不能包含 `SPEC_IR` 中不存在的架构字段。
- `GPU_STATE` 不能包含 candidate-only quality estimates。
- `synthesis_candidate_id` 只能用于追溯，不能影响执行语义。

### 增加的能力

state engine 能追踪 DESIGN 来源，但不会让 synthesis 的质量评分、候选排序或解释性字段污染执行状态。

## 10. 修改现有 Skill: `gpgpu-deterministic-transform-engine`

### 修改文件

- Modify: `skill/gpgpu-deterministic-transform-engine/SKILL.md`
- Modify: `skill/gpgpu-deterministic-transform-engine/SKILL.zh.md`

### v2 修改

新增 transform target：

```text
STATE_TO_VALIDATION
```

输出：

```text
validation_trace_schema
required_smoke_tests
counter_binding_table
artifact_coverage_report
```

### 增加的能力

closure engine 可以从 transform engine 获取应该验证哪些 trace、counter 和 artifact coverage，而不是临时猜测测试范围。

## 11. 修改现有 Skill: `gpgpu-config`

### 修改文件

- Modify: `skill/gpgpu-config/SKILL.md`
- Modify: `skill/gpgpu-config/SKILL.zh.md`

### v2 修改

正式引入 config 分类：

```text
hardware_private
simulator_private
hw_sw_abi
test_only
debug_only
```

新增检查：

- `hw_sw_abi` fields 必须出现在 runtime contract。
- `hardware_private` fields 不能被 runtime 修改。
- `simulator_private` fields 不能影响 RTL trace。
- `test_only` 和 `debug_only` fields 不能影响 canonical execution semantics。
- ABI-visible 常量不能只存在 RTL。

### 增加的能力

config skill 能阻止 ABI、RTL、simulator、debug/test 参数混用，避免 downstream artifact 各自解释 config。

## 12. 修改现有 Skill: `gpgpu-runtime`

### 修改文件

- Modify: `skill/gpgpu-runtime/SKILL.md`
- Modify: `skill/gpgpu-runtime/SKILL.zh.md`

### v2 修改

新增 smoke-test 输出：

```text
runtime_launch_smoke_report = {
  module_load,
  argument_layout,
  queue_submit,
  launch_admit,
  warp_start,
  completion_or_fault,
  verdict
}
```

### 增加的能力

runtime 不只解释 ABI，还能为 closure engine 提供最小 launch correctness 证据。

## 13. 修改现有 Skill: `gpgpu-memory-path`

### 修改文件

- Modify: `skill/gpgpu-memory-path/SKILL.md`
- Modify: `skill/gpgpu-memory-path/SKILL.zh.md`

### v2 修改

新增 memory consistency smoke：

```text
memory_ordering_smoke_report = {
  global_load_store,
  shared_memory_access,
  lane_mask,
  byte_enable,
  fence,
  atomic,
  outstanding_request_tag,
  verdict
}
```

### 增加的能力

memory skill 可以作为 closure gate 的证据来源，验证 memory state machine 是否能执行最小一致性场景。

## 14. 修改现有 Skill: `gpgpu-rtl-simt-core`

### 修改文件

- Modify: `skill/gpgpu-rtl-simt-core/SKILL.md`
- Modify: `skill/gpgpu-rtl-simt-core/SKILL.zh.md`

### v2 修改

新增 implementability report：

```text
rtl_implementability_report = {
  unsupported_state_fields,
  unmapped_fsm_rules,
  pipeline_hazards,
  scoreboard_conflicts,
  memory_interface_conflicts,
  verdict
}
```

### 增加的能力

RTL skill 可以判断当前 `GPU_STATE` 是否能被现有 RTL mapping 实现，但仍不能修改架构或重解释状态。

## 15. 修改现有 Skill: `gpgpu-golden-sim`

### 修改文件

- Modify: `skill/gpgpu-golden-sim/SKILL.md`
- Modify: `skill/gpgpu-golden-sim/SKILL.zh.md`

### v2 修改

新增 property-test 输出：

```text
property_test_report = {
  deterministic_replay,
  first_divergence_location,
  mandatory_semantic_field_coverage,
  verdict
}
```

### 保持不变的原则

`gpgpu-golden-sim` 仍然不是第二语义源。它检查 trace 是否遵循 `GPU_STATE` 和 transform table，不重新定义 ISA。

### 增加的能力

golden sim 可以为 closure engine 提供 deterministic replay 和 trace coverage 证据。

## 16. 修改现有 Skill: `gpgpu-causal-trace-analyzer`

### 修改文件

- Modify: `skill/gpgpu-causal-trace-analyzer/SKILL.md`
- Modify: `skill/gpgpu-causal-trace-analyzer/SKILL.zh.md`

### v2 修改

新增输出：

```text
REFINEMENT_REQUEST = {
  root_cause,
  affected_state_field,
  failed_gate,
  proposed_repair_type,
  evidence_trace
}
```

新增规则：

- causal analyzer 不能直接修改 `ARCH_IR`。
- causal analyzer 只能把失败原因交回 `gpgpu-synthesis-closure-engine`。
- repair 路由必须是 `synthesis-closure-engine -> architecture-synthesizer`。

### 增加的能力

性能和 trace 失败可以变成结构化 refinement request，DESIGN 模式因此具备闭环修复路径。

## 17. `skill_summary.md` 需要同步的内容

### 修改文件

- Modify: `skill/skill_summary.md`

### 建议修改

把当前单路径 summary 改成双路径 summary：

```text
REPRODUCE:
spec.md
 -> gpgpu-spec-lock
 -> SPEC_IR
 -> gpgpu-canonical-state-engine
 -> GPU_STATE
 -> deterministic artifacts
 -> validation

DESIGN:
user intent
 -> gpgpu-design-intent-lock
 -> DESIGN_INTENT_IR
 -> gpgpu-architecture-synthesizer
 -> ARCH_CANDIDATE + synthesized_spec_draft
 -> gpgpu-spec-lock
 -> SPEC_IR
 -> gpgpu-canonical-state-engine
 -> GPU_STATE
 -> deterministic artifacts
 -> gpgpu-synthesis-closure-engine
 -> ACCEPT / REFINE / REJECT
```

summary 中必须明确：

- synthesizer 不是 truth source。
- synthesized draft 必须经过 `spec-lock`。
- `GPU_STATE` 仍是 downstream 唯一 truth。
- closure engine 是 DESIGN 模式验收中心。

## 18. Regression Examples

### 建议新增文件

- Create: `skill/examples/reproduce/minimal_complete_spec.md`
- Create: `skill/examples/reproduce/illegal_missing_warp_size.md`
- Create: `skill/examples/design/minimal_simt_intent.md`
- Create: `skill/examples/design/fpga_small_gpgpu_intent.md`
- Create: `skill/examples/design/illegal_warp_size_33.md`
- Create: `skill/examples/design/memory_bandwidth_insufficient.md`

### 每个例子应包含

```text
input_kind
expected_path
expected_result
rejection_or_acceptance_reason
expected_first_gate
```

建议 expected result：

```text
PASS
REJECT_BY_SPEC_LOCK
REJECT_BY_HARD_CONSTRAINT
REFINE_REQUIRED_BY_QUALITY_GATE
```

## 19. v2 正确性保证

### 完整 spec 路径

```text
spec.md
 -> gpgpu-spec-lock
 -> SPEC_IR
 -> gpgpu-canonical-state-engine
 -> GPU_STATE
 -> gpgpu-deterministic-transform-engine
 -> validators
 -> acceptance report
```

保证：

- 同一个 spec 加同一个 enum table 会得到同一个 `SPEC_IR`。
- 同一个 `SPEC_IR` 会得到同一个 `GPU_STATE`。
- 同一个 `GPU_STATE` 和 transform table 会得到同一个 artifact。
- 不同 skill 不重新解释架构。
- trace divergence 可以定位到 state field 和 transition rule。

不保证：

- 输入 spec 本身性能最优。
- 用户给出的架构没有目标层面的缺陷。

这些需要 PPA gate、trace smoke、causal analyzer 和 quality target 判断。

### 从 0 设计路径

```text
user intent
 -> DESIGN_INTENT_IR
 -> ARCH_CANDIDATE
 -> synthesized_spec_draft
 -> SPEC_IR
 -> GPU_STATE
 -> artifacts
 -> validation reports
 -> ACCEPT / REFINE / REJECT
```

五层保证：

| 层 | 保证内容 |
|---|---|
| `gpgpu-design-intent-lock` | 目标、约束、non-goals 不漂移 |
| `gpgpu-architecture-synthesizer` | 只在固定模板和硬约束内生成候选 |
| `gpgpu-spec-lock` | 生成结果必须变成无歧义 `SPEC_IR` |
| `gpgpu-canonical-state-engine` | 架构事实必须变成合法 `GPU_STATE` |
| `gpgpu-synthesis-closure-engine` | 只有通过 coverage、state、artifact、trace、quality gate 的 candidate 才能接受 |

核心判断标准：

```text
设计生成器不可信；
闭环验收可信。
```

## 20. 新增能力总结

v2 相对 v1 增加这些能力：

- 从不完整设计意图生成合法候选 GPGPU。
- 用固定 preset 和 template library 限制设计空间。
- 用 `ARCH_IR` 表达 candidate design，而不是直接生成 truth。
- 用 field provenance 审计每个 synthesized value 来源。
- 用 closure gates 把 candidate 变成 `ACCEPT`、`REFINE_REQUIRED`、`REJECT` 或 `INSUFFICIENT_EVIDENCE`。
- 用 `STATE_TO_VALIDATION` 生成验证 trace schema、smoke tests 和 artifact coverage。
- 用 runtime、memory、RTL、golden、config validators 作为 closure evidence。
- 用 causal analyzer 生成结构化 `REFINEMENT_REQUEST`，形成设计修复回路。

## 21. 建议落地顺序

### Task 1: 新增 IR schema

**Files:**

- Create: `skill/references/ir/DESIGN_INTENT_IR.v1.md`
- Create: `skill/references/ir/ARCH_IR.v1.md`
- Create: `skill/references/ir/SYNTHESIS_ACCEPTANCE_REPORT.v1.md`
- Create: `skill/references/ir/FIELD_PROVENANCE.v1.md`

**Acceptance:**

- 四个 schema 明确字段、允许 enum、禁止来源和 hash/stability 要求。
- `ARCH_IR` 明确不是 `GPU_STATE`。

### Task 2: 修改 `gpgpu-mode-controller`

**Files:**

- Modify: `skill/gpgpu-mode-controller/SKILL.md`
- Modify: `skill/gpgpu-mode-controller/SKILL.zh.md`

**Acceptance:**

- 输出包含 `input_kind` 和 `forbidden_next_skills`。
- `DESIGN + DESIGN_INTENT` 路由到 `gpgpu-design-intent-lock`。
- `REPRODUCE` 禁止经过 `gpgpu-architecture-synthesizer`。

### Task 3: 新增 `gpgpu-design-intent-lock`

**Files:**

- Create: `skill/gpgpu-design-intent-lock/SKILL.md`
- Create: `skill/gpgpu-design-intent-lock/SKILL.zh.md`
- Create: `skill/gpgpu-design-intent-lock/agents/openai.yaml`

**Acceptance:**

- 只输出 `DESIGN_INTENT_IR`。
- 不选择任何架构参数。
- 支持固定 preset enum。

### Task 4: 新增 `gpgpu-architecture-synthesizer`

**Files:**

- Create: `skill/gpgpu-architecture-synthesizer/SKILL.md`
- Create: `skill/gpgpu-architecture-synthesizer/SKILL.zh.md`
- Create: `skill/gpgpu-architecture-synthesizer/agents/openai.yaml`

**Acceptance:**

- 只输出 `ARCH_CANDIDATE` 和 `synthesized_spec_draft`。
- 第一版只支持 `MINIMAL_SIMT_CORE` 和 `MULTI_WARP_SINGLE_SM`。
- 所有参数都有 provenance。
- hard constraint fail 时输出 rejected candidate。

### Task 5: 新增 `gpgpu-synthesis-closure-engine`

**Files:**

- Create: `skill/gpgpu-synthesis-closure-engine/SKILL.md`
- Create: `skill/gpgpu-synthesis-closure-engine/SKILL.zh.md`
- Create: `skill/gpgpu-synthesis-closure-engine/agents/openai.yaml`

**Acceptance:**

- 第一版实现 requirement coverage、spec round-trip、state invariant、artifact mapping 四个 gate。
- 输出 `SYNTHESIS_ACCEPTANCE_REPORT`。
- verdict 只允许 `ACCEPT`、`REJECT`、`REFINE_REQUIRED`、`INSUFFICIENT_EVIDENCE`。

### Task 6: 更新现有 validation skills

**Files:**

- Modify: `skill/gpgpu-config/SKILL.md`
- Modify: `skill/gpgpu-config/SKILL.zh.md`
- Modify: `skill/gpgpu-runtime/SKILL.md`
- Modify: `skill/gpgpu-runtime/SKILL.zh.md`
- Modify: `skill/gpgpu-memory-path/SKILL.md`
- Modify: `skill/gpgpu-memory-path/SKILL.zh.md`
- Modify: `skill/gpgpu-rtl-simt-core/SKILL.md`
- Modify: `skill/gpgpu-rtl-simt-core/SKILL.zh.md`
- Modify: `skill/gpgpu-golden-sim/SKILL.md`
- Modify: `skill/gpgpu-golden-sim/SKILL.zh.md`
- Modify: `skill/gpgpu-causal-trace-analyzer/SKILL.md`
- Modify: `skill/gpgpu-causal-trace-analyzer/SKILL.zh.md`

**Acceptance:**

- config 分类检查进入 `gpgpu-config`。
- runtime 输出 launch smoke report。
- memory 输出 ordering smoke report。
- RTL 输出 implementability report。
- golden sim 输出 property test report。
- causal analyzer 输出 refinement request，但不能修改 `ARCH_IR`。

### Task 7: 更新 summary 和 examples

**Files:**

- Modify: `skill/skill_summary.md`
- Create: `skill/examples/reproduce/minimal_complete_spec.md`
- Create: `skill/examples/reproduce/illegal_missing_warp_size.md`
- Create: `skill/examples/design/minimal_simt_intent.md`
- Create: `skill/examples/design/fpga_small_gpgpu_intent.md`
- Create: `skill/examples/design/illegal_warp_size_33.md`
- Create: `skill/examples/design/memory_bandwidth_insufficient.md`

**Acceptance:**

- summary 展示双路径。
- examples 覆盖 PASS、spec lock reject、hard constraint reject、quality refinement 四类结果。

## 22. 最小可行 v2 目标

v2 第一阶段不追求“生成最佳 GPU”，只追求：

```text
from zero -> one legal deterministic baseline GPGPU
```

最小通过路径：

```text
DESIGN_INTENT_IR
 -> single-SM multi-warp SIMT ARCH_CANDIDATE
 -> synthesized_spec_draft
 -> SPEC_IR
 -> GPU_STATE
 -> deterministic artifacts
 -> coverage + invariant + mapping gate pass
```

这能先验证系统结构正确。更复杂的多 SM、多级 cache、tensor extension、真实 PPA loop 可以在 closure gates 稳定后逐步加入。

## 23. 自检清单

- [ ] `SPEC_IR` 和 `GPU_STATE` 仍是唯一 truth。
- [ ] `gpgpu-architecture-synthesizer` 只产生 candidate。
- [ ] candidate 必须经过 `gpgpu-spec-lock`。
- [ ] `GPU_STATE` 不包含 candidate-only quality estimates。
- [ ] DESIGN 模式不直接把 incomplete intent 送入 `spec-lock`。
- [ ] REPRODUCE 模式不经过 synthesizer。
- [ ] 每个 synthesized field 都有 provenance。
- [ ] closure engine 能拒绝错误 candidate。
- [ ] causal analyzer 只能输出 refinement request，不能直接修架构。
