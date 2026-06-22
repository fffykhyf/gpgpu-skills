# GPGPU Skills 总结：IR-Centered Design Compiler

## 1. 总体定位

当前 `skill/` 中的 GPGPU skills 应被理解为一套 **IR-centered GPGPU design compiler**，而不是一组独立的设计经验文档。

核心流程是：

```text
自然语言 / spec.md
  ↓
多级 IR
  ↓
一系列 skill pass
  ↓
确定性 GPGPU 设计产物
  ↓
validation / closure / refinement
```

这里有一个关键边界：

```text
skill 不是 IR。
skill 是读取某种 IR、执行受限转换、输出另一种 IR 或验证报告的 compiler pass。
```

因此每个 skill 都必须回答：

- 输入什么 IR。
- 输出什么 IR 或 report。
- 允许修改什么。
- 禁止修改什么。
- 必须验证什么 invariant。
- 失败时如何 reject 或 route。
- 下游可以依赖哪些字段。

## 2. 核心原则

### 不设计单个巨大 IR

系统不应该把所有信息塞进一个巨大的 `GPGPU_IR`。正确结构是多级 IR：

```text
MODE_SELECTION_IR
    ↓
DESIGN_INTENT_IR
    ↓
ARCH_CANDIDATE_IR
    ↓
SPEC_IR
    ↓
GPU_STATE_IR
    ↓
ARTIFACT_IR / VALIDATION_REPORT_IR
    ↓
SYNTHESIS_ACCEPTANCE_REPORT_IR / REFINEMENT_REQUEST_IR
```

每一级 IR 只解决一个阶段的问题，不能把上游的设计理由、候选评分、论文解释或 debug 信息污染到下游执行状态。

### Truth Source 分层

| 阶段 | Truth source | 说明 |
|---|---|---|
| 复现路径 | `SPEC_IR` | 完整 spec 被锁定后的核心事实 |
| 下游执行 | `GPU_STATE_IR` | runtime / memory / RTL / golden sim 唯一状态真相 |
| 设计路径 | `ARCH_CANDIDATE_IR` 只是候选 | 必须经过 `spec-lock` 和 closure gates 才能接受 |
| 验证路径 | `VALIDATION_REPORT_IR` | 各 checker 输出证据，不重新定义架构 |

最重要的不变量是：

```text
architecture-synthesizer 不可信；
IR + validator + closure 才可信。
```

## 3. 多级 IR 角色

### `MODE_SELECTION_IR`

入口控制 IR，由 `gpgpu-mode-controller` 输出。

它描述请求应该走哪条路径：

```text
MODE_SELECTION_IR = {
  mode,
  input_kind,
  reason,
  next_skill,
  forbidden_next_skills
}
```

它不包含架构字段，不选择 warp size、cache、scheduler、ISA 或 memory hierarchy。

### `DESIGN_INTENT_IR`

用于从 0 开始设计。

它描述：

```text
我要设计什么
不做什么
面向什么 workload
目标平台是什么
性能 / 面积 / 验证目标是什么
```

它应该包含：

```text
objective
non_goals
workload_profile
target_platform
hard_constraints
soft_constraints
required_features
optional_features
validation_target
prototype_credibility_target
```

它不应该包含：

```text
warp size
SM count
cache size
ISA encoding
RTL pipeline
```

这些架构参数还没有被合成出来，不能在 intent lock 阶段提前猜。

### `ARCH_CANDIDATE_IR`

这是 `gpgpu-architecture-synthesizer` 的输出。

它描述一个可验证的候选架构：

```text
SM 数量
warp size
scheduler
register file
shared memory
memory hierarchy
ISA profile
runtime launch contract
config contract
quality estimate
constraint proof
requirement coverage
```

但它仍然不是最终 truth。它只能进入：

```text
ARCH_CANDIDATE_IR
  ↓
synthesized_spec_draft
  ↓
gpgpu-spec-lock
  ↓
SPEC_IR
```

### `SPEC_IR`

这是完整设计 spec 的锁定形式。

来源可以是：

```text
human spec.md
synthesized_spec_draft
```

输出必须满足：

```text
完整
无歧义
无 hidden default
所有 enum resolved
每个字段都有 provenance
```

`SPEC_IR` 是复现路径的核心 truth，也是生成 `GPU_STATE_IR` 的唯一输入。

### `GPU_STATE_IR`

这是 `gpgpu-canonical-state-engine` 的输出。

它是真正给 runtime / memory / RTL / golden sim 使用的唯一状态真相：

```text
GPU_STATE_IR = {
  PC,
  warp_state,
  active_mask,
  register_state,
  memory_state,
  CSR_state,
  launch_state,
  scheduler_state,
  scoreboard_state,
  memory_request_state,
  execution_pipeline_state
}
```

它不应该包含：

```text
设计理由
quality score
candidate ranking
论文式解释
framework view
```

### `ARTIFACT_IR`

这是 `gpgpu-deterministic-transform-engine` 对 `GPU_STATE_IR` 的下游映射结果。

典型输出包括：

```text
RTL_MAPPING_IR
SIM_BEHAVIOR_IR
RUNTIME_CONTRACT_IR
MEMORY_MODEL_IR
CONFIG_BINDING_IR
STATE_TO_VALIDATION_IR
```

它必须 table-driven。没有 table entry 的 enum 必须 fail closed，不能临时推断实现。

### `VALIDATION_REPORT_IR`

这是各 checker 的输出。

包括：

```text
config_report
runtime_launch_smoke_report
memory_ordering_smoke_report
rtl_implementability_report
golden_trace_report
artifact_coverage_report
```

这些 report 是 evidence，不是新的 architecture truth。

### `SYNTHESIS_ACCEPTANCE_REPORT_IR`

这是 `gpgpu-synthesis-closure-engine` 的验收输出：

```text
SYNTHESIS_ACCEPTANCE_REPORT_IR = {
  candidate_id,
  input_hash,
  spec_ir_hash,
  gpu_state_hash,
  gate_results,
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

### `REFINEMENT_REQUEST_IR`

这是 `gpgpu-causal-trace-analyzer` 在失败或性能异常时输出的修复请求：

```text
REFINEMENT_REQUEST_IR = {
  root_cause,
  affected_state_field,
  failed_gate,
  proposed_repair_type,
  evidence_trace
}
```

它只能描述原因和建议修复类型，不能直接修改 `ARCH_CANDIDATE_IR`、`SPEC_IR` 或 `GPU_STATE_IR`。

## 4. 双路径工作流

### REPRODUCE：完整 spec 复现

```text
user spec.md
  ↓
gpgpu-mode-controller
  ↓
MODE_SELECTION_IR(mode = REPRODUCE, input_kind = COMPLETE_SPEC)
  ↓
gpgpu-spec-lock
  ↓
SPEC_IR
  ↓
gpgpu-canonical-state-engine
  ↓
GPU_STATE_IR
  ↓
gpgpu-deterministic-transform-engine
  ↓
ARTIFACT_IR / validation plans
  ↓
config / runtime / memory / rtl / golden validators
  ↓
VALIDATION_REPORT_IR
```

这个路径解决的问题是：

```text
同一个 spec 不能一次生成一个样子，下一次又生成另一个样子。
```

稳定性条件：

```text
SPEC_IR hash 不变
GPU_STATE_IR hash 不变
transform table version 不变
= deterministic artifacts 不变
```

### DESIGN：从 0 开始设计

```text
user design intent
  ↓
gpgpu-mode-controller
  ↓
MODE_SELECTION_IR(mode = DESIGN, input_kind = DESIGN_INTENT)
  ↓
gpgpu-design-intent-lock
  ↓
DESIGN_INTENT_IR
  ↓
gpgpu-architecture-synthesizer
  ↓
ARCH_CANDIDATE_IR + synthesized_spec_draft
  ↓
gpgpu-spec-lock
  ↓
SPEC_IR
  ↓
gpgpu-canonical-state-engine
  ↓
GPU_STATE_IR
  ↓
gpgpu-deterministic-transform-engine
  ↓
ARTIFACT_IR / validation plans
  ↓
validators
  ↓
VALIDATION_REPORT_IR
  ↓
gpgpu-synthesis-closure-engine
  ↓
SYNTHESIS_ACCEPTANCE_REPORT_IR
```

这个路径解决的问题是：

```text
用户没有完整 spec 时，系统先锁定设计目标，再生成候选架构，再通过 spec-lock 和 closure gates 验证。
```

## 5. Skill Pass 职责

### `gpgpu-mode-controller`

```text
input:  user request
output: MODE_SELECTION_IR
```

职责：

- 判断 `REPRODUCE` 或 `DESIGN`。
- 判断 `input_kind = COMPLETE_SPEC | DESIGN_INTENT | PATCH_REQUEST | TRACE_DEBUG`。
- 指定 `next_skill` 和 `forbidden_next_skills`。

禁止：

- 不产生 `SPEC_IR`。
- 不产生 `GPU_STATE_IR`。
- 不选择架构参数。
- DESIGN 模式下，如果用户没有完整 architecture spec，不能直接路由到 `gpgpu-spec-lock`。

### `gpgpu-design-intent-lock`

```text
input:  natural-language design goal
output: DESIGN_INTENT_IR
```

职责：

- 锁定 objective、non-goals、workload、platform、constraints、validation target。
- 支持显式 preset，例如 `MINIMAL_TEACHING_GPGPU`、`FPGA_SMALL_GPGPU`、`RTL_SYNTHESIZABLE_BASELINE`。

禁止：

- 不输出 `SPEC_IR`。
- 不选择 warp size、SM count、cache policy、scheduler、ISA 或 memory hierarchy。
- 不把自然语言目标直接传给 synthesizer。

### `gpgpu-architecture-synthesizer`

```text
input:  DESIGN_INTENT_IR + preset library + constraint table + enum table
output: ARCH_CANDIDATE_IR + synthesized_spec_draft
```

职责：

- 从固定 template library 中选择候选架构。
- 分配参数并记录 provenance。
- 检查 hard constraints。
- 输出 rejected alternatives、constraint proof、quality estimate 和 unresolved risks。

禁止：

- 不直接输出 `GPU_STATE_IR`。
- 不绕过 `gpgpu-spec-lock`。
- 不使用 `COMMON_GPU_DEFAULT`、`MODEL_GUESS` 或 `UNKNOWN` provenance。
- hard constraint 失败时不能包装成可接受设计。

### `gpgpu-spec-lock`

```text
input:  spec.md or synthesized_spec_draft
output: SPEC_IR
```

职责：

- 把 human spec 或 synthesized draft 锁成完整、无歧义 `SPEC_IR`。
- 解析 source kind：`HUMAN_SPEC | SYNTHESIZED_SPEC_DRAFT`。
- 确保每个 field 有 provenance。

禁止：

- 不补 implicit defaults。
- 不留下 unresolved enums。
- 不把 prose 传给 state engine。
- 不接受 provenance 为 `UNKNOWN` 的 synthesized field。

### `gpgpu-canonical-state-engine`

```text
input:  SPEC_IR
output: GPU_STATE_IR
```

职责：

- 把 locked spec 转成唯一 deterministic GPU state machine。
- 提供 `init(spec_ir)`、`apply(event)`、`transition(rule_id)`、`validate_invariants()`、`snapshot()`。
- 检查 PC、warp、mask、register、scoreboard、memory request、launch、CSR 等状态不变量。

禁止：

- 不做 architecture planning。
- 不吸收 candidate-only quality estimate。
- 不根据 RTL 或 runtime 便利性修改状态定义。

### `gpgpu-deterministic-transform-engine`

```text
input:  GPU_STATE_IR
output: ARTIFACT_IR / mapping reports / STATE_TO_VALIDATION_IR
```

职责：

- 把 `GPU_STATE_IR` table-driven 映射到 RTL、sim、runtime、memory、config、validation。
- 输出 mapping table version、state hash、artifact coverage report。
- 为 closure engine 生成 required smoke tests 和 validation trace schema。

禁止：

- 不做 LLM inference-based design。
- 不做 heuristic mapping。
- 没有 table entry 时不能临时合成实现。

### `gpgpu-config`

```text
input:  SPEC_IR.config_defaults + GPU_STATE_IR + CONFIG_BINDING_IR
output: config_report
```

职责：

- 检查 config 分类：`hardware_private`、`simulator_private`、`hw_sw_abi`、`test_only`、`debug_only`。
- 确保 ABI-visible 常量进入 runtime contract。
- 确保 test/debug/simulator-only 字段不影响 canonical execution semantics。

禁止：

- 不生成新的架构默认值。
- 不把 generated config 当 source of truth。

### `gpgpu-runtime`

```text
input:  GPU_STATE_IR + RUNTIME_CONTRACT_IR + kernel launch
output: execution_trace + runtime_launch_smoke_report
```

职责：

- 解释 kernel launch semantics、argument layout、command queue、doorbell、completion/fault。
- 输出 runtime launch smoke evidence。

禁止：

- 不推断 scheduler。
- 不优化 memory hierarchy。
- 不修改 `GPU_STATE_IR`。

### `gpgpu-memory-path`

```text
input:  GPU_STATE_IR.memory_state + MEMORY_MODEL_IR + memory events
output: memory_trace + memory_ordering_smoke_report
```

职责：

- 执行 cache behavior、memory hierarchy、coalescing、load/store/atomic/fence、bandwidth model。
- 检查 lane mask、byte enable、outstanding request tag、ordering violation。

禁止：

- 不选择 cache policy。
- 不改 memory hierarchy。
- 不做 speculative design。

### `gpgpu-rtl-simt-core`

```text
input:  GPU_STATE_IR + RTL_MAPPING_IR + kernel
output: cycle_level_simulation + hardware_trace + rtl_implementability_report
```

职责：

- 执行 scheduler FSM、pipeline、scoreboard、execution units、memory interface、CSR/fault。
- 报告 unsupported state fields、unmapped FSM rules、pipeline hazards、scoreboard conflicts。

禁止：

- 不 reinterpret architecture。
- 不因为 RTL 更容易实现而改 `GPU_STATE_IR`。

### `gpgpu-golden-sim`

```text
input:  GPU_STATE_IR + SIM_BEHAVIOR_IR + simulator_trace
output: golden_trace_report + property_test_report
```

职责：

- 检查 deterministic replay。
- 定位 first divergence。
- 检查 mandatory semantic field coverage。

禁止：

- 不作为第二语义源。
- 不重新定义 ISA。
- 不为了匹配 RTL 修改 simulator semantics。

### `gpgpu-synthesis-closure-engine`

```text
input:  ARCH_CANDIDATE_IR + SPEC_IR + GPU_STATE_IR + all validation reports
output: SYNTHESIS_ACCEPTANCE_REPORT_IR
```

职责：

- 汇总 coverage、round-trip、state invariant、artifact mapping、config lock、trace smoke、quality、stability gates。
- 输出 `ACCEPT`、`REJECT`、`REFINE_REQUIRED` 或 `INSUFFICIENT_EVIDENCE`。

禁止：

- 不设计架构。
- 不绕过 failed gate。
- 不接受没有 provenance 或证据不足的 candidate。

### `gpgpu-causal-trace-analyzer`

```text
input:  failed validation report / trace delta
output: REFINEMENT_REQUEST_IR
```

职责：

- 从 metric delta 追到 trace event delta。
- 从 trace event delta 追到 `GPU_STATE_IR` field 和 transition rule。
- 输出 root cause、affected field、failed gate、repair type 和 evidence trace。

禁止：

- 不直接修改 `ARCH_CANDIDATE_IR`。
- 不直接修改 `SPEC_IR`。
- 不直接修改 `GPU_STATE_IR`。

## 6. 每个 `SKILL.md` 应使用的固定模板

每个 GPGPU skill 的 `SKILL.md` 应改成 pass 规范，而不是 framework 视角集合。

固定结构：

```text
# Skill Role

# Input IR

# Output IR

# Allowed Transformations

# Forbidden Actions

# Required Invariants

# Failure Modes

# Report Schema

# Downstream Contract
```

必须删除或降级这种结构：

```text
## framework-specific view A
## framework-specific view B
## vendor-specific view
## paper-specific method
```

替换为：

```text
## Design Evidence Layer

- behavioral evidence: GPGPU-Sim
- structural reference: Rocket Chip / Vortex
- ISA / ABI constraint: PTX / CUDA
- empirical justification: papers
```

这些 evidence 只能用于验证 contract、解释 tradeoff 或锚定实现，不能成为章节组织方式，也不能覆盖 IR truth。

## 7. 正确性保证

### 完整 spec 复现

复现路径的稳定性来自：

```text
spec.md
  ↓
SPEC_IR
  ↓
GPU_STATE_IR
  ↓
deterministic artifacts
```

只要：

```text
SPEC_IR hash 不变
GPU_STATE_IR hash 不变
transform table version 不变
```

输出就应该稳定。

这保证：

- 不漂移。
- 不猜默认值。
- 不同 skill 不重新解释架构。
- trace divergence 可以定位。
- spec 变动可以 field-level diff。

它不保证：

- 输入 spec 本身性能最好。
- 用户给的架构目标合理。

这些需要 validation reports、closure gates 和 causal analyzer 判断。

### 从 0 开始设计

设计路径的正确性来自：

```text
DESIGN_INTENT_IR
  ↓
ARCH_CANDIDATE_IR
  ↓
synthesized_spec_draft
  ↓
SPEC_IR
  ↓
GPU_STATE_IR
  ↓
closure validation
```

五层约束：

| 层 | 保证什么 |
|---|---|
| `gpgpu-design-intent-lock` | 目标、约束、non-goals 不漂移 |
| `gpgpu-architecture-synthesizer` | 只在固定模板、enum table 和 hard constraints 内生成候选 |
| `gpgpu-spec-lock` | 生成结果必须变成完整、无歧义、有 provenance 的 `SPEC_IR` |
| `gpgpu-canonical-state-engine` | 所有架构事实必须变成合法 `GPU_STATE_IR` |
| `gpgpu-synthesis-closure-engine` | 只有通过 coverage、state、artifact、trace、quality gates 的 candidate 才能接受 |

最终可信的是：

```text
错误 candidate 无法通过 closure gates。
```

## 8. Failure Routing

| 问题 | 失败位置 | 路由 |
|---|---|---|
| 请求类型不清 | `gpgpu-mode-controller` | reject 或要求明确 `input_kind` |
| 设计目标缺字段 | `gpgpu-design-intent-lock` | reject 或要求显式 preset |
| candidate hard constraint 失败 | `gpgpu-architecture-synthesizer` | 输出 rejected candidate |
| synthesized field provenance 不明 | `gpgpu-spec-lock` | reject |
| spec 缺字段或歧义 | `gpgpu-spec-lock` | reject |
| state invariant 失败 | `gpgpu-canonical-state-engine` | reject 并报告 invalid field |
| transform table 缺 entry | `gpgpu-deterministic-transform-engine` | fail closed |
| config ownership 错 | `gpgpu-config` | 输出 config report failure |
| runtime launch 错 | `gpgpu-runtime` | 输出 runtime smoke failure |
| memory ordering 错 | `gpgpu-memory-path` | 输出 memory smoke failure |
| RTL 无法实现 | `gpgpu-rtl-simt-core` | 输出 implementability failure |
| sim / RTL trace 分歧 | `gpgpu-golden-sim` | 输出 first divergence |
| 性能或行为退化 | `gpgpu-causal-trace-analyzer` | 输出 `REFINEMENT_REQUEST_IR` |
| evidence 不足 | `gpgpu-synthesis-closure-engine` | `INSUFFICIENT_EVIDENCE` |

## 9. 增加的能力

这套结构相对经验型 skill 集合新增了这些能力：

- 从完整 `spec.md` 稳定复现同一个 GPGPU。
- 从不完整设计意图生成可验证的 architecture candidate。
- 用多级 IR 分离目标、候选、spec、执行状态、artifact 和验证证据。
- 用 provenance 阻止 hidden default 和模型猜测。
- 用 table-driven transform 保证 downstream artifacts 可复现。
- 用 validation reports 把 runtime、memory、RTL、golden、config 都变成 evidence pass。
- 用 closure engine 统一做 `ACCEPT / REJECT / REFINE_REQUIRED / INSUFFICIENT_EVIDENCE`。
- 用 causal analyzer 把失败 trace 转成结构化 refinement request。

## 10. 最终一句话

这套系统的目标不是把每个 skill 都做成 IR，而是把整个 GPGPU skill 系统重构为：

```text
多级 IR + skill pass + invariant + provenance + closure validation
```

这样它既能稳定复现一个已有 spec，也能从 0 开始生成一个可验证的 GPGPU 设计。
