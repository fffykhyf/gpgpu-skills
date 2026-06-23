# GPGPU Skill Self-Correcting Design System Implementation Plan

> 2026-06-23 更新：本文件最初记录 5-stage 压缩方案。当前流程已升级为 6-stage，在 `System Contract + Golden Semantics Engine` 和 `Incremental RTL Binding Engine` 之间新增 `gpgpu-runtime`，负责从 `SYSTEM_CONTRACT_IR` 派生 assembler、disassembler、program image、runtime launch artifact 和 loader contract。后续实施以 `README.md` 和 `shared/flow/gpgpu_design_flow.md` 中的 6-stage flow 为准。

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前 GPGPU skill flow 从“IR-driven design pipeline”升级为“self-correcting design system”：可以生成架构、冻结合同、执行 golden semantics、派生 toolchain/runtime artifacts、增量绑定 RTL、归因性能/正确性问题，并自动产生 architecture / contract / toolchain / RTL rewrite plan。

**Architecture:** 当前系统由 6 个核心模块组成：Architecture Generator、System Contract + Golden Semantics Engine、Toolchain + Runtime Artifact Engine、Incremental RTL Binding Engine、Simulation + Performance Attribution Engine、Architecture Rewrite Loop Controller。核心变化是补齐 5 个工程缺口：Executable Golden Model、toolchain/runtime artifact stage、module-by-module incremental RTL、Performance Attribution Graph、Architecture Rewriting Trigger。

**Tech Stack:** Markdown skills, `SKILL.md` / optional `SKILL.zh.md`, YAML schemas, YAML rule tables, executable reference-model specifications, module interface contracts, trace normalization rules, regression cases under `shared/tests/`, example IR under `shared/examples/`, validation script under `shared/tests/validate_v4_assets.py` or later `validate_v5_assets.py`.

---

## 先校准：当前计划的真实状态

上一版计划已经把 9-stage 压缩成一个更合理的 4-layer system：

```text
(1) Architecture Generator
(2) System Contract Core
(3) RTL Binding Layer
(4) Performance + Closure Loop
```

这个方向是对的，但仍然停在“结构压缩”和“report-driven closure”。它还没有变成真正的 self-correcting design system。缺口集中在四处：

| 缺口 | 当前状态 | 必须补齐的工程实体 |
|---|---|---|
| Executable Golden Model | contract 只定义，不执行 | `GOLDEN_CONTRACT_MODEL` |
| Incremental RTL | RTL mapping 偏全局生成 | `INCREMENTAL_RTL_MAP` + module interface checker |
| Performance Attribution | 只有 perf report | `PERF_ATTRIBUTION_GRAPH` |
| Architecture Rewrite Trigger | closure 只报告 | `ARCH_REWRITE_PLAN` |

因此本计划不再把目标描述为“旧压缩 pipeline”，而是明确升级为：

```text
(1) Architecture Generator
        ↓
(2) System Contract + Golden Semantics Engine
        ↓
(3) Toolchain + Runtime Artifact Engine
        ↓
(4) Incremental RTL Binding Engine
        ↓
(5) Simulation + Performance Attribution Engine
        ↓
(6) Architecture Rewrite Loop Controller
        ↺ back to (1)(2)(3)
```

## 核心原则

### 1. Contract 必须可执行

合同不是只给人读的定义，也不是只给 validator 引用的静态字段。合同必须能 lowering 成可执行 reference semantics：

- execution contract -> warp scheduling, divergence, scoreboard-visible semantics
- memory contract -> ordering, coalescing, fence, atomic, request lifecycle reference functions
- launch contract -> ABI decode, grid/block/thread mapping, kernel entry semantics
- config contract -> visible/private/test/debug field semantics

输出的 `GOLDEN_CONTRACT_MODEL` 是 reference model，不是第二套 simulator。它只能执行 `SYSTEM_CONTRACT_IR` 中已经冻结的语义，不能重新定义 ISA、memory ordering、warp model 或 launch ABI。

### 2. RTL 必须模块级增量收敛

全局 `RTL_MAP` 不够。真实 GPU 设计需要 module-by-module assembly，并且每个模块都有 local trace、local scoreboard check、interface contract check。

RTL 绑定必须拆成：

- SM core RTL
- warp scheduler RTL
- execution pipeline RTL
- register file / scoreboard RTL
- load/store queue RTL
- shared memory RTL
- cache / global memory interface RTL
- interconnect / CSR / runtime interface RTL

输出的 `INCREMENTAL_RTL_MAP` 必须记录每个 module 的接口、依赖、local simulation evidence、边界延迟、handshake 规则和 unresolved binding risk。

### 3. 性能报告必须升级为因果图

perf report 只说明慢，不说明为什么慢，也不能指导自动修复。需要构造跨层因果链：

```text
cycle
  -> warp
  -> scoreboard dependency
  -> memory request
  -> cache miss / bank conflict / ordering wait
  -> RTL pipeline stage
  -> contract rule
```

输出的 `PERF_ATTRIBUTION_GRAPH` 必须把 stall、divergence、memory pressure、pipeline bubble、scheduler inefficiency 映射到 contract path 和 RTL module path。

### 4. Closure 必须升级为 rewrite controller

Closure report 只能告诉用户发生了什么。self-correcting design system 还必须产生可执行的修复计划：

- Architecture Patch: warp size、SM partition、memory hierarchy、scheduler class、issue width
- Contract Patch: scheduling rule、memory ordering、launch ABI、scoreboard semantics
- RTL Patch: pipeline boundary、scoreboard redesign、LSQ replay policy、cache interface

输出的 `ARCH_REWRITE_PLAN` 不能直接改 truth，但必须给出 owner、patch target、expected impact、required revalidation gates 和 regression risk。

## 最终模块结构

| 新模块 | 原 skill 来源 | 新增关键能力 | 主要输出 |
|---|---|---|---|
| `gpgpu-arch` | `gpgpu-front-end` + `gpgpu-architecture-synthesizer` | Micro-constraint estimator | `DESIGN_INTENT_IR`, `ARCH_IR`, `MICRO_CONSTRAINT_ESTIMATE_IR` |
| `gpgpu-golden` | `gpgpu-spec-lock` + `gpgpu-canonical-state-engine` + truth part of `gpgpu-artifact-contract-engine` | Contract executable semantics engine | `SYSTEM_CONTRACT_IR`, `GOLDEN_CONTRACT_MODEL` |
| `gpgpu-rtl` | binding part of `gpgpu-artifact-contract-engine` + structural part of `gpgpu-memory-subsystem` | Module-by-module RTL builder, interface checker, partial simulator | `INCREMENTAL_RTL_MAP`, `MODULE_INTERFACE_REPORT` |
| `gpgpu-simppa` | `gpgpu-runtime-validator` + `gpgpu-memory-subsystem` validation + `gpgpu-implementation-validator` | Trace normalizer, bottleneck graph builder, root cause engine | `NORMALIZED_TRACE_IR`, `PERF_ATTRIBUTION_GRAPH`, `ROOT_CAUSE_REPORT` |
| `gpgpu-loop` | `gpgpu-closure-refinement-engine` + causal trace analyzer behavior | Architecture / contract / RTL rewrite trigger | `ARCH_REWRITE_PLAN`, `REGRESSION_TRACKING_REPORT` |

`reader` 保持为只读证据支持 skill，不进入生成闭环。`legacy/` 中的旧 skill 不再保留；它们的有用约束被迁移到新 owner skill 的 `legacy_*_constraints.md` 引用文件中，避免旧 skill 继续成为可调用的第二套流程。

## Module 1: Architecture Generator

### 目标

把用户意图、约束、preset、参考证据转换为候选 architecture graph，同时提前估计不可实现风险。

### 合并来源

- `gpgpu-front-end`
- `gpgpu-architecture-synthesizer`

### 新增子系统：Micro-Constraint Estimator

该 estimator 在生成候选架构时同步输出微架构约束估计，避免候选后期才发现不可实现。

输入：

- `DESIGN_INTENT_IR`
- preset library
- workload profile
- target platform
- hard constraints
- historical reference lessons

输出：

- `area_estimate`
- `memory_pressure_estimate`
- `warp_occupancy_bound`
- `register_pressure_bound`
- `shared_memory_pressure_bound`
- `minimum_bandwidth_need`
- `known_unrealizable_risks`

### 输出 IR

```text
DESIGN_INTENT_IR
ARCH_IR
MICRO_CONSTRAINT_ESTIMATE_IR
ARCH_GENERATION_REPORT
```

### 正确性规则

- `ARCH_IR` 是候选 graph，不是 system truth。
- micro-constraint estimate 是 bound 和 risk，不是最终 PPA truth。
- 缺 workload、platform、validation target 时必须 reject 或要求显式 preset。
- 每个架构参数必须有 provenance。
- 禁止 `MODEL_GUESS`、`COMMON_GPU_DEFAULT`、`UNKNOWN` 作为参数来源。

### 需要创建的 skill

`skill/gpgpu-arch/SKILL.md`

必须包含：

```text
Role
Position in Flow
Input IR
Output IR
Owned Decisions
Forbidden Actions
Required Tables
Required Schemas
Required Invariants
Failure Modes
Report Schema
Concrete Assets Required
```

## Module 2: System Contract + Golden Semantics Engine

### 目标

把 architecture graph 冻结成系统合同，并生成可执行 reference semantics。这里是系统 truth 的唯一来源。

### 合并来源

- `gpgpu-spec-lock`
- `gpgpu-canonical-state-engine`
- `gpgpu-artifact-contract-engine` 的 truth/source-of-truth/config 部分
- `gpgpu-runtime-validator` 的 launch truth 部分
- `gpgpu-memory-subsystem` 的 memory truth 部分

### 新增子系统：Contract Executable Semantics Engine

这个子系统把 `SYSTEM_CONTRACT_IR` lowering 成 `GOLDEN_CONTRACT_MODEL`。它不是 RTL simulator，也不是新的 ISA 解释器；它只执行合同中已经冻结的语义。

Execution semantics:

- warp scheduling rule
- active mask update rule
- divergence and reconvergence rule
- scoreboard dependency rule
- pipeline-visible commit rule

Memory semantics:

- address space resolver
- coalescing reference function
- byte-enable reference function
- ordering rule engine
- fence and atomic reference function
- request lifecycle reference function

Launch semantics:

- ABI decode function
- grid/block/thread mapping function
- kernel entry resolver
- CSR-visible launch state transition
- completion/fault observation rule

### 输出 IR

```text
SYSTEM_CONTRACT_IR
GOLDEN_CONTRACT_MODEL
CONTRACT_SEMANTICS_REPORT
```

### 正确性规则

- `SYSTEM_CONTRACT_IR` 是唯一 truth source。
- `GOLDEN_CONTRACT_MODEL` 必须引用 `SYSTEM_CONTRACT_IR` hash。
- `GOLDEN_CONTRACT_MODEL` 不能拥有独立 ISA、memory、launch、scheduler truth。
- 每个 executable semantics function 必须映射到 contract path。
- 未映射 contract path 必须 fail closed。
- hidden default、unknown enum、duplicate truth owner、forbidden provenance 必须 reject。

### 需要创建的 skill

`skill/gpgpu-golden/SKILL.md`

### 需要新增 references

- `skill/gpgpu-golden/contract_truth_and_state_model.md`
- `skill/gpgpu-golden/executable_semantics_rules.md`
- `skill/gpgpu-golden/golden_model_coverage_and_report.md`

## Module 3: Incremental RTL Binding Engine

### 目标

把 `SYSTEM_CONTRACT_IR` 和 `GOLDEN_CONTRACT_MODEL` 逐模块绑定到 RTL 结构，而不是一次性生成全局 RTL map。

### 合并来源

- `gpgpu-artifact-contract-engine` 的 RTL lowering 部分
- `gpgpu-memory-subsystem` 的 RTL-facing memory path 部分
- `gpgpu-runtime-validator` 的 runtime/CSR hardware interface 部分
- `gpgpu-implementation-validator` 的 implementability gate 部分

### 新增子系统 3.1：Module-by-Module RTL Builder

模块列表：

- `sm_core`
- `warp_scheduler`
- `decode_execute_pipeline`
- `register_file`
- `scoreboard`
- `load_store_queue`
- `coalescer`
- `shared_memory_bank_unit`
- `l1_cache_or_global_adapter`
- `memory_response_router`
- `fault_completion_unit`
- `interconnect`
- `csr_runtime_interface`

每个 module 输出：

- module contract
- consumed contract paths
- provided signals
- required signals
- latency contract
- local state bindings
- local trace schema
- local simulation evidence

### 新增子系统 3.2：Interface Contract Checker

检查：

- signal consistency
- handshake correctness
- valid/ready or req/resp protocol
- latency compatibility
- pipeline boundary correctness
- reset semantics
- stall/backpressure propagation
- width and tag consistency

### 新增子系统 3.3：RTL Partial Simulator

每个 module 必须可以局部模拟，输出：

- local sim trace
- local scoreboard check
- interface transaction trace
- mismatch report against `GOLDEN_CONTRACT_MODEL` slice

### 输出 IR

```text
INCREMENTAL_RTL_MAP
MODULE_INTERFACE_REPORT
RTL_PARTIAL_SIM_REPORT
```

### 正确性规则

- 每个 RTL module 必须引用 `SYSTEM_CONTRACT_IR` path。
- 每个 RTL module 必须声明 consumed/provided interface。
- interface mismatch 必须阻止进入全系统 RTL simulation。
- partial simulation 不能替代全系统 verification，只能作为 module gate。
- RTL binding 不能修改合同语义。

### 需要创建的 skill

`skill/gpgpu-rtl/SKILL.md`

### 需要新增 references

- `skill/gpgpu-rtl/module_binding_rules.md`
- `skill/gpgpu-rtl/interface_binding_and_checker.md`
- `skill/gpgpu-rtl/partial_simulation_gates.md`
- `skill/gpgpu-rtl/rtl_module_catalog.md`

## Module 4: Simulation + Performance Attribution Engine

### 目标

把 runtime trace、RTL trace、golden trace、memory trace 统一成可比较的 normalized trace，并构造性能/正确性因果图。

### 合并来源

- `gpgpu-runtime-validator`
- `gpgpu-memory-subsystem` 的 validation 部分
- `gpgpu-implementation-validator`
- `gpgpu-closure-refinement-engine` 的 causal trace analysis 部分

### 新增子系统 4.1：Trace Normalizer

统一输入：

- RTL trace
- waveform-derived trace
- golden contract trace
- runtime launch trace
- memory trace
- module partial sim trace

输出：

- `NORMALIZED_TRACE_IR`
- trace event dictionary
- event-to-contract-path map
- event-to-rtl-module map
- timestamp/cycle normalization report

### 新增子系统 4.2：Bottleneck Graph Builder

构建因果链：

```text
warp_stall
  -> scoreboard_dependency
  -> memory_request
  -> cache_miss / bank_conflict / ordering_wait
  -> rtl_pipeline_stage
  -> contract_rule
```

节点类型：

- cycle window
- warp
- instruction
- contract rule
- RTL module
- memory request
- scoreboard dependency
- pipeline stage
- bottleneck category

边类型：

- caused_by
- blocked_by
- waits_for
- violates
- maps_to
- amplified_by

### 新增子系统 4.3：Root Cause Engine

输出 root cause class：

- `CONTRACT_VIOLATION`
- `RTL_STRUCTURAL_ISSUE`
- `MEMORY_IMBALANCE`
- `SCHEDULING_INEFFICIENCY`
- `INTERFACE_PROTOCOL_MISMATCH`
- `GOLDEN_MODEL_MISMATCH`
- `INSUFFICIENT_TRACE_EVIDENCE`

### 输出 IR

```text
NORMALIZED_TRACE_IR
PERF_ATTRIBUTION_GRAPH
ROOT_CAUSE_REPORT
SIM_PERF_ATTRIBUTION_REPORT
```

### 正确性规则

- perf attribution 必须有 trace evidence。
- 每个 bottleneck node 必须能追溯到 contract path 或 RTL module path。
- 没有因果链时输出 `INSUFFICIENT_TRACE_EVIDENCE`。
- golden trace 只来自 `GOLDEN_CONTRACT_MODEL`，不能来自另一个未受控 simulator。
- root cause 必须包含最小可复现 trace window。

### 需要创建的 skill

`skill/gpgpu-simppa/SKILL.md`

### 需要新增 references

- `skill/gpgpu-simppa/trace_ingestion_and_normalization.md`
- `skill/gpgpu-simppa/correctness_gate_and_mode_selection.md`
- `skill/gpgpu-simppa/pass_evidence_engine.md`
- `skill/gpgpu-simppa/performance_metric_extractor.md`
- `skill/gpgpu-simppa/bottleneck_graph_builder.md`
- `skill/gpgpu-simppa/root_cause_engine.md`

## Module 5: Architecture Rewrite Loop Controller

### 目标

把 closure 从“最终报告”升级为“自动设计修复控制器”。它读取 `PERF_ATTRIBUTION_GRAPH`、`INCREMENTAL_RTL_MAP`、`SYSTEM_CONTRACT_IR` 和 `ARCH_IR`，生成 architecture / contract / RTL patch plan，并触发回到 Module 1/2/3。

### 合并来源

- `gpgpu-closure-refinement-engine`
- `legacy/gpgpu-synthesis-closure-engine`
- `legacy/gpgpu-causal-trace-analyzer`

### 新增能力：Architecture Rewriting Trigger

输入：

- `PERF_ATTRIBUTION_GRAPH`
- `ROOT_CAUSE_REPORT`
- `INCREMENTAL_RTL_MAP`
- `SYSTEM_CONTRACT_IR`
- `GOLDEN_CONTRACT_MODEL`
- `ARCH_IR`
- regression history

输出三类 patch：

Architecture Patch:

- warp size change
- SM partition change
- issue width change
- memory hierarchy change
- scheduler class change

Contract Patch:

- scheduling rule change
- memory ordering change
- launch ABI change
- scoreboard semantic change
- coalescing semantic change

RTL Patch:

- pipeline re-layout
- scoreboard redesign
- LSQ replay policy change
- interface latency adjustment
- cache/global interface redesign

### 输出 IR

```text
ARCH_REWRITE_PLAN
REWRITE_DECISION_REPORT
REGRESSION_TRACKING_REPORT
```

### 正确性规则

- rewrite controller 不能直接改 IR 文件，只能输出 patch plan。
- 每个 patch 必须指向 owner module。
- 每个 patch 必须声明 expected impact 和 required revalidation gates。
- architecture patch 必须回到 Module 1。
- contract patch 必须回到 Module 2。
- RTL patch 必须回到 Module 3。
- 所有 patch 都必须触发 Module 4 重新归因验证。

### 需要创建的 skill

`skill/gpgpu-loop/SKILL.md`

### 需要新增 references

- `skill/gpgpu-loop/rewrite_trigger.md`
- `skill/gpgpu-loop/patch_taxonomy.md`
- `skill/gpgpu-loop/regression_tracking.md`
- `skill/gpgpu-loop/revalidation_routing.md`

## 现有 skill 迁移策略

| 当前 skill | 新 owner | 迁移方式 |
|---|---|---|
| `gpgpu-front-end` | `gpgpu-arch` | 迁移 intent intake 约束后删除旧 skill |
| `gpgpu-architecture-synthesizer` | `gpgpu-arch` | 迁移 candidate generation 约束后删除旧 skill |
| `gpgpu-spec-lock` | `gpgpu-golden` | 迁移 truth freeze 到 system contract |
| `gpgpu-canonical-state-engine` | `gpgpu-golden` | 迁移 state semantics 到 executable golden semantics |
| `gpgpu-artifact-contract-engine` | `gpgpu-golden` + `gpgpu-rtl` | truth part 进 Module 2，binding part 进 Module 3 |
| `gpgpu-runtime-validator` | `gpgpu-golden` + `gpgpu-simppa` | launch semantics 进 Module 2，runtime trace validation 进 Module 4 |
| `gpgpu-memory-subsystem` | Module 2 + Module 3 + Module 4 | memory truth、memory binding、memory correctness 分拆 |
| `gpgpu-implementation-validator` | `gpgpu-rtl` + `gpgpu-simppa` | module gates 进 Module 3，全系统 diff 进 Module 4 |
| `gpgpu-closure-refinement-engine` | `gpgpu-loop` | 从 closure report 改为 rewrite loop controller |

旧 top-level skills 和 `legacy/` 旧 skill 不保留为 active wrapper。迁移完成后必须删除旧目录，并由校验脚本禁止旧 skill 回流。

## 新 schemas

### Module 1 schemas

- `skill/shared/schemas/arch_ir.schema.yaml`
- `skill/shared/schemas/micro_constraint_estimate_ir.schema.yaml`
- `skill/shared/schemas/arch_generation_report_ir.schema.yaml`

`micro_constraint_estimate_ir.schema.yaml` 必须包含：

```yaml
required:
  - area_estimate
  - memory_pressure_estimate
  - warp_occupancy_bound
  - register_pressure_bound
  - shared_memory_pressure_bound
  - minimum_bandwidth_need
  - known_unrealizable_risks
```

### Module 2 schemas

- `skill/shared/schemas/system_contract_ir.schema.yaml`
- `skill/shared/schemas/golden_contract_model.schema.yaml`
- `skill/shared/schemas/contract_semantics_report_ir.schema.yaml`

`golden_contract_model.schema.yaml` 必须包含：

```yaml
required:
  - system_contract_ir_hash
  - execution_semantics_functions
  - memory_semantics_functions
  - launch_semantics_functions
  - config_semantics_functions
  - contract_path_coverage
  - forbidden_independent_truth_check
```

### Module 3 schemas

- `skill/shared/schemas/incremental_rtl_map.schema.yaml`
- `skill/shared/schemas/module_interface_report_ir.schema.yaml`
- `skill/shared/schemas/rtl_partial_sim_report_ir.schema.yaml`

`incremental_rtl_map.schema.yaml` 必须包含：

```yaml
required:
  - system_contract_ir_hash
  - golden_contract_model_hash
  - modules
  - module_interfaces
  - consumed_contract_paths
  - provided_signal_paths
  - local_trace_schemas
  - unresolved_binding_risks
```

### Module 4 schemas

- `skill/shared/schemas/normalized_trace_ir.schema.yaml`
- `skill/shared/schemas/perf_attribution_graph.schema.yaml`
- `skill/shared/schemas/root_cause_report_ir.schema.yaml`
- `skill/shared/schemas/sim_perf_attribution_report_ir.schema.yaml`

`perf_attribution_graph.schema.yaml` 必须包含：

```yaml
required:
  - graph_id
  - trace_window
  - nodes
  - edges
  - contract_path_index
  - rtl_module_path_index
  - bottleneck_summary
  - evidence_hashes
```

### Module 5 schemas

- `skill/shared/schemas/arch_rewrite_plan.schema.yaml`
- `skill/shared/schemas/rewrite_decision_report_ir.schema.yaml`
- `skill/shared/schemas/regression_tracking_report_ir.schema.yaml`

`arch_rewrite_plan.schema.yaml` 必须包含：

```yaml
required:
  - rewrite_id
  - trigger_root_cause
  - patch_type
  - patch_targets
  - owner_module
  - expected_impact
  - required_revalidation_gates
  - regression_risks
```

## 新 tables

| 文件 | 责任 |
|---|---|
| `skill/shared/tables/micro_constraint_estimator_table.yaml` | area / memory pressure / occupancy bound 估计规则 |
| `skill/shared/tables/contract_semantics_binding_table.yaml` | contract path 到 executable semantics function 的映射 |
| `skill/shared/tables/golden_model_coverage_table.yaml` | golden model 覆盖 gate |
| `skill/shared/tables/rtl_module_catalog.yaml` | module-by-module RTL builder 的模块目录 |
| `skill/shared/tables/module_interface_contract_table.yaml` | signal、handshake、latency、pipeline boundary 规则 |
| `skill/shared/tables/rtl_partial_sim_gate_table.yaml` | module partial simulation gate |
| `skill/shared/tables/trace_normalization_table.yaml` | RTL/golden/runtime/memory trace normalization |
| `skill/shared/tables/perf_attribution_taxonomy.yaml` | bottleneck graph node/edge 分类 |
| `skill/shared/tables/root_cause_taxonomy.yaml` | root cause class 和证据要求 |
| `skill/shared/tables/rewrite_trigger_table.yaml` | root cause 到 patch type 的触发规则 |
| `skill/shared/tables/patch_taxonomy_table.yaml` | architecture/contract/RTL patch 分类 |
| `skill/shared/tables/revalidation_routing_table.yaml` | patch 后必须重跑的 module/gate |

## 新 tests 和 examples

### Tests

新增：

- `skill/shared/tests/architecture_generator/cases.yaml`
- `skill/shared/tests/system_contract_golden_engine/cases.yaml`
- `skill/shared/tests/incremental_rtl_binding_engine/cases.yaml`
- `skill/shared/tests/simulation_performance_attribution_engine/cases.yaml`
- `skill/shared/tests/architecture_rewrite_loop_controller/cases.yaml`

每个 test case 必须包含：

```yaml
case_id:
input_artifacts:
expected_outputs:
expected_failure_mode:
required_evidence:
forbidden_outputs:
```

### Examples

新增：

- `skill/shared/examples/self_correcting_minimal_simt/input_request.md`
- `skill/shared/examples/self_correcting_minimal_simt/expected_arch_ir.yaml`
- `skill/shared/examples/self_correcting_minimal_simt/expected_micro_constraint_estimate.yaml`
- `skill/shared/examples/self_correcting_minimal_simt/expected_system_contract_ir.yaml`
- `skill/shared/examples/self_correcting_minimal_simt/expected_golden_contract_model.yaml`
- `skill/shared/examples/self_correcting_minimal_simt/expected_incremental_rtl_map.yaml`
- `skill/shared/examples/self_correcting_minimal_simt/expected_perf_attribution_graph.yaml`
- `skill/shared/examples/self_correcting_minimal_simt/expected_arch_rewrite_plan.yaml`

示例必须覆盖一个明确场景：memory pressure 触发 warp occupancy bound，随后 RTL partial sim 发现 LSQ backpressure，Module 4 归因为 memory imbalance，Module 5 输出 architecture patch 或 RTL patch。

## 实施任务

### Task 1: 更新总览文档为 self-correcting system

**Files:**

- Modify: `skill/skill_5stage_compression_plan.zh.md`
- Later modify: `skill/README.md`
- Later modify: `skill/skill_summary.md`
- Later modify: `skill/shared/flow/gpgpu_design_flow.md`

- [ ] **Step 1: Replace compression-only framing**

  Replace old wording:

  ```text
  single IR graph + multi-pass lowering + verification loop
  ```

  with:

  ```text
  self-correcting design system with executable golden semantics, incremental RTL binding, performance attribution graph, and architecture rewrite loop
  ```

- [ ] **Step 2: Add final flow**

  Add:

  ```text
  Architecture Generator
    -> System Contract + Golden Semantics Engine
    -> Incremental RTL Binding Engine
    -> Simulation + Performance Attribution Engine
    -> Architecture Rewrite Loop Controller
    -> back to Architecture Generator / Contract / RTL Binding
  ```

- [ ] **Step 3: Preserve deletion note**

  State that old 9-stage and legacy skills were deleted after useful constraints were migrated into `legacy_*_constraints.md` references.

### Task 2: Create new top-level skill skeletons

**Files:**

- Create: `skill/gpgpu-arch/SKILL.md`
- Create: `skill/gpgpu-golden/SKILL.md`
- Create: `skill/gpgpu-rtl/SKILL.md`
- Create: `skill/gpgpu-simppa/SKILL.md`
- Create: `skill/gpgpu-loop/SKILL.md`

- [ ] **Step 1: Create `gpgpu-arch`**

  Required invariant:

  ```text
  ARCH_IR is a candidate graph. MICRO_CONSTRAINT_ESTIMATE_IR is a feasibility estimate. This skill must not emit system contract truth, golden semantics, RTL bindings, performance attribution, or rewrite patches.
  ```

- [ ] **Step 2: Create `gpgpu-golden`**

  Required invariant:

  ```text
  SYSTEM_CONTRACT_IR is the only semantic truth source. GOLDEN_CONTRACT_MODEL is executable reference semantics derived from SYSTEM_CONTRACT_IR and must not define independent ISA, memory, launch, scheduler, or config truth.
  ```

- [ ] **Step 3: Create `gpgpu-rtl`**

  Required invariant:

  ```text
  INCREMENTAL_RTL_MAP binds modules one by one. Every module must declare consumed contract paths, provided signals, required signals, latency contract, local trace schema, and partial simulation evidence.
  ```

- [ ] **Step 4: Create `gpgpu-simppa`**

  Required invariant:

  ```text
  PERF_ATTRIBUTION_GRAPH must connect cycle, warp, memory, contract path, and RTL module evidence. A performance conclusion without this causal chain must be INSUFFICIENT_TRACE_EVIDENCE.
  ```

- [ ] **Step 5: Create `gpgpu-loop`**

  Required invariant:

  ```text
  ARCH_REWRITE_PLAN may propose architecture, contract, or RTL patches, but must not directly mutate ARCH_IR, SYSTEM_CONTRACT_IR, GOLDEN_CONTRACT_MODEL, INCREMENTAL_RTL_MAP, or traces.
  ```

### Task 3: Add executable golden semantics assets

**Files:**

- Create: `skill/gpgpu-golden/contract_truth_and_state_model.md`
- Create: `skill/gpgpu-golden/executable_semantics_rules.md`
- Create: `skill/gpgpu-golden/golden_model_coverage_and_report.md`
- Create: `skill/shared/schemas/golden_contract_model.schema.yaml`
- Create: `skill/shared/tables/contract_semantics_binding_table.yaml`
- Create: `skill/shared/tables/golden_model_coverage_table.yaml`

- [ ] **Step 1: Define execution semantics mapping**

  Each execution rule must have:

  ```text
  contract_path
  semantics_function
  input_fields
  output_fields
  deterministic_rule_id
  failure_mode
  ```

- [ ] **Step 2: Define memory semantics mapping**

  Include reference functions for:

  ```text
  address_space_resolve
  coalesce
  byte_enable
  fence_order
  atomic_apply
  request_lifecycle_step
  ```

- [ ] **Step 3: Define launch semantics mapping**

  Include reference functions for:

  ```text
  abi_decode
  grid_block_thread_map
  kernel_entry_resolve
  completion_or_fault_observe
  ```

### Task 4: Add incremental RTL assets

**Files:**

- Create: `skill/gpgpu-rtl/module_binding_rules.md`
- Create: `skill/gpgpu-rtl/interface_binding_and_checker.md`
- Create: `skill/gpgpu-rtl/partial_simulation_gates.md`
- Create: `skill/gpgpu-rtl/rtl_module_catalog.md`
- Create: `skill/shared/schemas/incremental_rtl_map.schema.yaml`
- Create: `skill/shared/tables/rtl_module_catalog.yaml`
- Create: `skill/shared/tables/module_interface_contract_table.yaml`
- Create: `skill/shared/tables/rtl_partial_sim_gate_table.yaml`

- [ ] **Step 1: Define module catalog**

  Required modules:

  ```text
  sm_core
  warp_scheduler
  decode_execute_pipeline
  register_file
  scoreboard
  load_store_queue
  coalescer
  shared_memory_bank_unit
  l1_cache_or_global_adapter
  memory_response_router
  fault_completion_unit
  interconnect
  csr_runtime_interface
  ```

- [ ] **Step 2: Define interface checker fields**

  Each interface check must include:

  ```text
  signal_width
  direction
  valid_ready_or_req_resp
  latency_min
  latency_max
  reset_value
  backpressure_rule
  trace_tap
  ```

- [ ] **Step 3: Define partial simulation gate**

  Each module partial sim must output:

  ```text
  local_trace_hash
  local_scoreboard_result
  interface_transaction_result
  golden_slice_compare_result
  verdict
  ```

### Task 5: Add performance attribution graph assets

**Files:**

- Create: `skill/gpgpu-simppa/trace_ingestion_and_normalization.md`
- Create: `skill/gpgpu-simppa/correctness_gate_and_mode_selection.md`
- Create: `skill/gpgpu-simppa/pass_evidence_engine.md`
- Create: `skill/gpgpu-simppa/performance_metric_extractor.md`
- Create: `skill/gpgpu-simppa/bottleneck_graph_builder.md`
- Create: `skill/gpgpu-simppa/root_cause_engine.md`
- Create: `skill/shared/schemas/perf_attribution_graph.schema.yaml`
- Create: `skill/shared/tables/trace_normalization_table.yaml`
- Create: `skill/shared/tables/perf_attribution_taxonomy.yaml`
- Create: `skill/shared/tables/root_cause_taxonomy.yaml`

- [ ] **Step 1: Define normalized trace event**

  Required fields:

  ```text
  event_id
  cycle
  warp_id
  instruction_id
  contract_path
  rtl_module_path
  event_type
  dependencies
  evidence_source
  ```

- [ ] **Step 2: Define bottleneck graph node classes**

  Required classes:

  ```text
  cycle_window
  warp
  instruction
  scoreboard_dependency
  memory_request
  cache_event
  bank_conflict
  rtl_pipeline_stage
  contract_rule
  bottleneck_category
  ```

- [ ] **Step 3: Define root cause output**

  Required fields:

  ```text
  root_cause_class
  minimal_trace_window
  contract_paths
  rtl_module_paths
  evidence_hashes
  confidence
  rewrite_candidate
  ```

### Task 6: Add architecture rewrite loop assets

**Files:**

- Create: `skill/gpgpu-loop/rewrite_trigger.md`
- Create: `skill/gpgpu-loop/patch_taxonomy.md`
- Create: `skill/gpgpu-loop/regression_tracking.md`
- Create: `skill/gpgpu-loop/revalidation_routing.md`
- Create: `skill/shared/schemas/arch_rewrite_plan.schema.yaml`
- Create: `skill/shared/tables/rewrite_trigger_table.yaml`
- Create: `skill/shared/tables/patch_taxonomy_table.yaml`
- Create: `skill/shared/tables/revalidation_routing_table.yaml`

- [ ] **Step 1: Define rewrite triggers**

  Required trigger mapping:

  ```text
  MEMORY_IMBALANCE -> Architecture Patch or RTL Patch
  SCHEDULING_INEFFICIENCY -> Architecture Patch or Contract Patch
  RTL_STRUCTURAL_ISSUE -> RTL Patch
  CONTRACT_VIOLATION -> Contract Patch
  INTERFACE_PROTOCOL_MISMATCH -> RTL Patch
  GOLDEN_MODEL_MISMATCH -> Contract Patch or Golden Semantics Bug
  ```

- [ ] **Step 2: Define patch taxonomy**

  Patch classes:

  ```text
  ARCHITECTURE_PATCH
  CONTRACT_PATCH
  RTL_PATCH
  TEST_EVIDENCE_PATCH
  ```

- [ ] **Step 3: Define revalidation routing**

  Required routing:

  ```text
  ARCHITECTURE_PATCH -> Module 1 -> Module 2 -> Module 3 -> Module 4
  CONTRACT_PATCH -> Module 2 -> Module 3 -> Module 4
  RTL_PATCH -> Module 3 -> Module 4
  TEST_EVIDENCE_PATCH -> Module 4
  ```

### Task 7: Migrate and delete old skills

**Files:**

- Create or update: `skill/gpgpu-arch/legacy_request_and_candidate_constraints.md`
- Create or update: `skill/gpgpu-golden/contract_truth_and_state_model.md`
- Create or update: `skill/gpgpu-rtl/module_binding_rules.md`
- Create or update: `skill/gpgpu-simppa/legacy_validation_and_trace_constraints.md`
- Create or update: `skill/gpgpu-loop/legacy_closure_repair_constraints.md`
- Delete: old top-level `skill/gpgpu-*` directories that are not one of the six current v5 skills.
- Delete: `skill/legacy/` old skill archive after useful constraints are migrated.

- [ ] **Step 1: Migrate useful constraints**

  Move useful behavior into the six current owner skill reference files:

- request classification, mode routing, and design-intent lock -> Architecture Generator
- spec/state/config truth and golden trace replay -> System Contract + Golden Semantics Engine
- assembler/disassembler derivation, program image, runtime launch, and loader artifacts -> Toolchain + Runtime Artifact Engine
- deterministic transform, module binding, memory path structure, and RTL implementability -> Incremental RTL Binding Engine
- runtime, memory, RTL/golden trace, and causal attribution evidence -> Simulation + Performance Attribution Engine
- closure gates, repair routing, regression risk, and rewrite decisions -> Architecture Rewrite Loop Controller

- [ ] **Step 2: Delete old skill directories**

  Remove the old top-level skill directories and `skill/legacy/` after migration.

- [ ] **Step 3: Add regression guard**

  Update `shared/tests/validate_v4_assets.py` so old skill directories and the v4 generator fail validation if they reappear.

### Task 8: Update validator to check the self-correcting system contract

**Files:**

- Modify: `skill/shared/tests/validate_v4_assets.py`
- Optional rename after migration: `skill/shared/tests/validate_v5_assets.py`

- [ ] **Step 1: Replace top-level skill list**

  New top-level list:

  ```python
  TOP_LEVEL_SKILLS = [
      "gpgpu-arch",
      "gpgpu-golden",
      "gpgpu-rtl",
      "gpgpu-simppa",
      "gpgpu-loop",
  ]
  ```

- [ ] **Step 2: Add required text checks**

  Required text:

  ```python
  V5_REQUIRED_TEXT = {
      "gpgpu-golden/SKILL.md": [
          "GOLDEN_CONTRACT_MODEL",
          "executable reference semantics",
          "must not define independent ISA",
      ],
      "gpgpu-rtl/SKILL.md": [
          "module by module",
          "Interface Contract Checker",
          "RTL Partial Simulator",
      ],
      "gpgpu-simppa/SKILL.md": [
          "PERF_ATTRIBUTION_GRAPH",
          "cycle",
          "contract path",
          "RTL module",
      ],
      "gpgpu-loop/SKILL.md": [
          "ARCH_REWRITE_PLAN",
          "Architecture Patch",
          "Contract Patch",
          "RTL Patch",
      ],
  }
  ```

- [ ] **Step 3: Require new schemas and tables**

  Add all schemas and tables listed in this plan to the validator.

### Task 9: Update examples to prove the closed loop

**Files:**

- Create: `skill/shared/examples/self_correcting_minimal_simt/input_request.md`
- Create: `skill/shared/examples/self_correcting_minimal_simt/expected_arch_ir.yaml`
- Create: `skill/shared/examples/self_correcting_minimal_simt/expected_micro_constraint_estimate.yaml`
- Create: `skill/shared/examples/self_correcting_minimal_simt/expected_system_contract_ir.yaml`
- Create: `skill/shared/examples/self_correcting_minimal_simt/expected_golden_contract_model.yaml`
- Create: `skill/shared/examples/self_correcting_minimal_simt/expected_incremental_rtl_map.yaml`
- Create: `skill/shared/examples/self_correcting_minimal_simt/expected_perf_attribution_graph.yaml`
- Create: `skill/shared/examples/self_correcting_minimal_simt/expected_arch_rewrite_plan.yaml`

- [ ] **Step 1: Create loop scenario**

  The example must describe:

  ```text
  minimal SIMT GPU request
  memory pressure estimate
  LSQ backpressure in partial RTL sim
  normalized trace showing warp stall
  perf attribution graph linking stall to memory request and RTL pipeline stage
  architecture or RTL rewrite plan
  ```

- [ ] **Step 2: Keep v4 examples as compatibility evidence**

  Move old v4 expected outputs to:

  ```text
  skill/shared/examples/v4_compat/
  ```

  Keep them until the v5 validator passes.

### Task 10: Final verification

**Files:**

- Modify: `skill/README.md`
- Modify: `skill/skill_summary.md`
- Modify: `skill/shared/flow/gpgpu_design_flow.md`

- [ ] **Step 1: Run content coverage checks**

  Run:

  ```bash
  rg "GOLDEN_CONTRACT_MODEL|INCREMENTAL_RTL_MAP|PERF_ATTRIBUTION_GRAPH|ARCH_REWRITE_PLAN" skill
  ```

  Expected: all four core outputs appear in top-level skills, schemas, tests, examples, and summary docs.

- [ ] **Step 2: Run validator**

  Run:

  ```bash
  python3 skill/shared/tests/validate_v4_assets.py
  ```

  Expected after migration:

  ```text
  GPGPU skill v5 self-correcting asset contract passed
  ```

- [ ] **Step 3: Check old wording is no longer active**

  Run:

  ```bash
  rg "closure report only|global RTL_MAP|perf report only|contract only defines" skill
  ```

  Expected: no active skill presents the old incomplete behavior as current.

## Verification matrix

| User-identified gap | New component | Required artifact |
|---|---|---|
| No Executable Golden Model | System Contract + Golden Semantics Engine | `GOLDEN_CONTRACT_MODEL` |
| RTL is global/generative | Incremental RTL Binding Engine | `INCREMENTAL_RTL_MAP` |
| No Performance Attribution Graph | Simulation + Performance Attribution Engine | `PERF_ATTRIBUTION_GRAPH` |
| No Architecture Rewriting Trigger | Architecture Rewrite Loop Controller | `ARCH_REWRITE_PLAN` |
| Infeasible architectures detected late | Architecture Generator | `MICRO_CONSTRAINT_ESTIMATE_IR` |
| Closure only reports | Rewrite loop controller | patch routing and revalidation gates |

## Non-goals

- Do not keep old v4 or legacy skills as active wrappers after their useful constraints are migrated.
- Do not make `GOLDEN_CONTRACT_MODEL` a second truth source.
- Do not make partial RTL simulation a replacement for full-system verification.
- Do not accept perf conclusions without causal graph evidence.
- Do not let rewrite controller mutate IR directly; it outputs patch plans and routes revalidation.

## Recommended implementation order

1. Keep the 6 current top-level skills as the active namespace.
2. Add executable golden semantics schemas, tables, and references.
3. Add toolchain/runtime artifact schemas, tables, references, and smoke examples.
4. Add incremental RTL binding schemas, tables, and references.
5. Add trace normalization and performance attribution graph schemas, tables, and references.
6. Add rewrite loop schemas, tables, and references.
7. Migrate useful old-skill constraints into the six v5 skills, then delete old skill directories.
8. Update validator and examples.
9. Update README, summary, and flow docs.
10. Run validation and only then archive old v4 directories.
