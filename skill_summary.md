# GPGPU Skills 总结

## 1. 总体定位

当前 `skill/` 中的 GPGPU skills 不再是一组松散的“设计建议文档”，而是一套 **GPGPU state compiler**。

它的核心原则是：

```text
自然语言 spec
  -> 锁定后的 SPEC_IR
  -> 唯一 canonical GPU_STATE
  -> table-driven downstream artifacts
  -> runtime / memory / RTL / simulator traces
  -> causal trace analysis
```

也就是说，系统不允许每个 skill 自己“理解架构”或“重新设计架构”。所有设计事实必须先进入 `SPEC_IR`，再由 `GPU_STATE` 作为唯一 truth source 向下游传播。

## 2. 整体依赖结构

强制主链路如下：

```text
gpgpu-mode-controller
   ↓
gpgpu-spec-lock
   ↓
gpgpu-canonical-state-engine
   ↓
gpgpu-deterministic-transform-engine
   ↓
runtime / memory / rtl / simulator / config validators
   ↓
gpgpu-causal-trace-analyzer
```

各层职责边界：

| 层级 | 作用 | 不能做什么 |
|---|---|---|
| mode | 选择 `REPRODUCE` 或 `DESIGN` | 不参与状态、映射、设计决策 |
| spec lock | 把自然语言 spec 锁成无歧义 `SPEC_IR` | 不补隐式默认值，不做架构推断 |
| state engine | 把 `SPEC_IR` 转成唯一 `GPU_STATE` | 不做规划、不做评估、不做启发式设计 |
| transform engine | 把 `GPU_STATE` 变成下游 artifact | 不做 LLM 推断式设计，不做 heuristic mapping |
| execution layers | 执行 runtime / memory / RTL / simulator 行为并产出 trace | 不改 `GPU_STATE`，不重新解释架构 |
| causal analyzer | 从 trace delta 解释性能或行为变化的原因 | 不报空洞 metrics，不给无因果链结论 |

## 3. 每个 Skill 的职责

### `gpgpu-mode-controller`

入口 skill，只负责决定当前请求运行在哪个模式：

```text
MODE = REPRODUCE | DESIGN
```

- `REPRODUCE`：严格复现已有 spec、trace、paper、config、bug 或结果。
- `DESIGN`：在约束下合成新设计，但仍必须经过 spec lock 和确定性状态生成。

它不产生 `SPEC_IR`，不产生 `GPU_STATE`，不选择 cache、scheduler、memory model 或 ISA 细节。

### `gpgpu-spec-lock`

负责稳定输入，把 `spec.md` 或用户自然语言说明转成结构化 `SPEC_IR`：

```text
SPEC_IR = {
  ISA: canonical,
  warp_model: explicit,
  memory_hierarchy: explicit,
  scheduling_policy: explicit,
  config_defaults: resolved
}
```

关键规则：

- 不允许 implicit defaults。
- 不允许 natural language ambiguity。
- 不允许 unresolved enums。
- 所有默认值必须显式、可追溯。
- 冲突或缺失字段必须 reject，不能猜。

### `gpgpu-canonical-state-engine`

核心 state engine，负责唯一转换：

```text
SPEC_IR -> GPU_STATE
```

输出的 `GPU_STATE` 包含：

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

它提供 FSM API：

| API | 作用 |
|---|---|
| `init(spec_ir)` | 从 locked `SPEC_IR` 初始化完整 `GPU_STATE` |
| `apply(event)` | 应用一个事件 |
| `transition(rule_id)` | 执行一个确定的 transition rule |
| `validate_invariants()` | 检查状态不变量 |
| `snapshot()` | 输出可序列化、可 diff 的状态快照 |

这个 skill 是系统的中心。下游所有 skill 只能消费它输出的 `GPU_STATE`，不能重新定义状态。

### `gpgpu-deterministic-transform-engine`

负责把 `GPU_STATE` 映射到所有下游 artifact：

```text
GPU_STATE -> RTL_MAPPING | SIM_BEHAVIOR | RUNTIME_CONTRACT | MEMORY_MODEL | PPA_MODEL
```

它必须 table-driven：

| `GPU_STATE` enum | 映射要求 |
|---|---|
| `warp_sched_type` | 映射到唯一 scheduler implementation |
| `cache_policy` | 映射到唯一 cache behavior table |
| `memory_model` | 映射到唯一 ordering/bandwidth model |
| `issue_policy` | 映射到唯一 issue/scoreboard mapping |
| `exec_unit_type` | 映射到唯一 latency/port/trace mapping |
| `launch_abi_version` | 映射到唯一 runtime layout |

如果 table 中没有对应 enum，必须 fail closed，不能临时合成实现。

### `gpgpu-runtime`

runtime skill 已收缩为“执行语义解释器”：

```text
input:  GPU_STATE + kernel_launch
output: execution_trace
```

它只解释：

- kernel launch semantics。
- ABI layout。
- command queue。
- event / fence / completion / fault。
- ABI-visible warp execution semantics。

它不做 architecture assumptions，不推断 scheduler，不优化 memory。

### `gpgpu-memory-path`

memory skill 已收缩为 memory execution model：

```text
input:  GPU_STATE.memory_state + memory_events
output: memory_trace
```

它只执行 `GPU_STATE.memory_state` 中已经定义好的：

- cache behavior。
- memory hierarchy execution。
- bandwidth model。
- load/store/atomic/fence behavior。
- fault / replay / ordering behavior。

它不选择 cache policy，不改 memory hierarchy，不做 speculative design。

### `gpgpu-rtl-simt-core`

RTL SIMT skill 已收缩为 pure hardware execution model：

```text
input:  GPU_STATE + kernel
output: cycle_level_simulation + hardware_trace
```

它执行 transform engine 已经映射好的硬件模型：

- scheduler FSM。
- fetch / decode / issue / execute / writeback pipeline。
- scoreboard。
- execution unit latency/port。
- memory interface events。
- CSR/fault behavior。

它不能 reinterpret architecture，不能修改 `GPU_STATE`，不能因为 RTL 更容易实现就改变状态定义。

### `gpgpu-golden-sim`

golden sim skill 已变成 simulator artifact validator，不再是第二个 semantic oracle：

```text
input:  GPU_STATE + SIM_BEHAVIOR + simulator_trace
output: sim_validation_report
```

它检查 simulator trace 是否遵循：

- `GPU_STATE` snapshot hash。
- transform table version。
- declared trace schema。
- state-machine transition sequence。

如果 simulator 和 RTL 不一致，它报告 first divergence，但不修改 simulator semantics 来迎合 RTL。

### `gpgpu-config`

config skill 已变成 config lock validator：

```text
input:  SPEC_IR.config_defaults + GPU_STATE
output: config_lock_report
```

它检查：

- config default 是否来自 `SPEC_IR.config_defaults`。
- enum 是否已由 `gpgpu-spec-lock` resolve。
- config field 是否绑定到唯一 `GPU_STATE` 字段。
- generated artifact 是否引用 transform table version 和 state hash。

它不再生成 config，不再补默认值，不再把 generated config 当 source of truth。

### `gpgpu-causal-trace-analyzer`

PPA/evaluation skill 已重命名并改造成 causal layer：

```text
performance_delta -> state_transition_cause
```

它从 trace delta 反推原因：

```text
metric delta
  -> trace event delta
  -> GPU_STATE field delta
  -> transition(rule_id)
  -> root cause
```

支持的核心分析：

- warp stall cause tracing。
- memory bottleneck attribution。
- scheduling inefficiency root cause。
- execution-unit pressure。
- launch overhead。

如果因果链断裂，必须输出 `TRACE_INSUFFICIENT`，不能猜。

## 4. 系统如何工作

### Step 1：选择模式

用户请求先进入 `gpgpu-mode-controller`。

- 如果目标是复现已有结果，进入 `REPRODUCE`。
- 如果目标是按约束生成新设计，进入 `DESIGN`。

无论哪种模式，都不能跳过后续 lock 和 state engine。

### Step 2：锁定输入

`gpgpu-spec-lock` 将自然语言 spec 转为 `SPEC_IR`。这一层解决输入不稳定问题。

所有字段必须显式：

- ISA。
- warp model。
- memory hierarchy。
- scheduling policy。
- config defaults。

缺字段时拒绝，不猜。

### Step 3：生成唯一状态

`gpgpu-canonical-state-engine` 把 `SPEC_IR` 转成 `GPU_STATE`。

这是系统唯一的架构状态来源。之后所有 runtime、memory、RTL、sim、config、PPA 行为都必须从它派生。

### Step 4：确定性映射

`gpgpu-deterministic-transform-engine` 使用固定 mapping table，把 `GPU_STATE` 转成：

- RTL mapping。
- simulator behavior。
- runtime contract。
- memory model。
- PPA model。

mapping 缺失时 fail closed。

### Step 5：执行与验证

下游 skill 不再设计，只执行：

- `gpgpu-runtime` 产生 launch/execution trace。
- `gpgpu-memory-path` 产生 memory trace。
- `gpgpu-rtl-simt-core` 产生 cycle-level hardware trace。
- `gpgpu-golden-sim` 验证 simulator artifact。
- `gpgpu-config` 验证 config lock。

### Step 6：因果解释

`gpgpu-causal-trace-analyzer` 对 trace delta 或 performance delta 做 cause-effect mapping。

它不只说“慢了”或“快了”，而是指出：

- 哪个 trace event 变化了。
- 哪个 `GPU_STATE` 字段变化了。
- 哪个 `transition(rule_id)` 导致变化。
- root cause 属于哪个固定 cause enum。

## 5. 如何保证生成的设计是正确的

这套系统用多层约束保证 correctness。

### 1. 输入正确性：`SPEC_IR` 锁定

`gpgpu-spec-lock` 保证输入没有自然语言歧义：

- no implicit defaults。
- no unresolved enums。
- no ambiguous prose。
- no hidden assumptions。

这防止后续 skill 因为“理解不同”产生 drift。

### 2. 状态正确性：唯一 `GPU_STATE`

`gpgpu-canonical-state-engine` 保证所有架构事实都进入统一状态机：

- warp_state。
- scheduler_state。
- memory_state。
- register_state。
- execution_units。
- launch_state。
- csr_state。

通过 `validate_invariants()` 检查：

- warp PC 和 active mask 是否唯一。
- active mask 宽度是否匹配 warp model。
- scoreboard dependency 是否引用合法 register。
- outstanding memory request tag 是否唯一。
- launch resource 是否超过 resolved defaults。

### 3. 转换正确性：table-driven mapping

`gpgpu-deterministic-transform-engine` 保证 state 到 artifact 的转换不是 LLM 猜测：

- 每个 enum 只能有一个 mapping。
- 每个 consumed state field 必须 mapped 或 explicit unused。
- artifact 必须带 mapping table version 和 state hash。
- 重复运行必须 byte-stable。

### 4. 执行正确性：trace 可回溯

runtime、memory、RTL、simulator 层都必须输出 trace，并且 trace event 必须能回溯到：

- `GPU_STATE` snapshot hash。
- transform rule ID。
- state field。
- event ordering。

这保证错误不是最终才暴露，而是能定位到 first divergence。

### 5. 解释正确性：因果链完整

`gpgpu-causal-trace-analyzer` 要求每个性能或行为判断都有完整链路：

```text
metric delta
  -> trace event delta
  -> GPU_STATE field delta
  -> transition(rule_id)
  -> root cause
```

链路不完整时，输出 `TRACE_INSUFFICIENT`，不能给结论。

## 6. 当前系统的关键变化

旧系统中，每个 skill 都有一定“理解能力”，容易产生 drift：

```text
skill chain = pipeline
每个 skill 都可能重新解释设计
```

当前系统中，skill chain 是 compiler：

```text
skill chain = compiler
SPEC_IR 和 GPU_STATE 是唯一 truth
每一步 deterministic
缺信息就 fail closed
```

最关键的变化是：

> 设计不是由下游 skill 推断出来的，而是由 locked spec 生成唯一状态，再由固定表确定性展开。

因此，这套 skill 的目标不是“帮助写一个 GPU 设计说明”，而是把 GPGPU 设计过程约束成一个可验证、可 diff、可追责的 state compiler。
