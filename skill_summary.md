# GPGPU Skill v5 总结

`skill/` 当前定义的是一个 self-correcting GPGPU design system。它已经删除旧 9-stage 顶层 skill、旧 `legacy/` skill 归档、旧示例、旧 IR reference、v4-only schemas/tables/tests，只保留当前 v5 闭环需要的资产。

## 五个核心 skill

| Skill | 责任 | 核心输出 |
|---|---|---|
| `gpgpu-architecture-generator` | 读取用户意图、锁定设计目标、生成候选架构，并提前估计不可实现风险 | `MODE_SELECTION_IR`, `DESIGN_INTENT_IR`, `ARCH_IR`, `MICRO_CONSTRAINT_ESTIMATE_IR` |
| `gpgpu-system-contract-golden-engine` | 冻结唯一系统合同，并从合同派生可执行 golden semantics | `SYSTEM_CONTRACT_IR`, `GOLDEN_CONTRACT_MODEL`, `CONTRACT_SEMANTICS_REPORT` |
| `gpgpu-incremental-rtl-binding-engine` | 把系统合同逐模块绑定到 RTL，并做 interface check 与 partial simulation | `INCREMENTAL_RTL_MAP`, `MODULE_INTERFACE_REPORT`, `RTL_PARTIAL_SIM_REPORT` |
| `gpgpu-simulation-performance-attribution-engine` | 归一化 runtime/memory/RTL/golden trace，构造性能和正确性因果图 | `NORMALIZED_TRACE_IR`, `PERF_ATTRIBUTION_GRAPH`, `ROOT_CAUSE_REPORT` |
| `gpgpu-architecture-rewrite-loop-controller` | 根据 root cause 产生 architecture/contract/RTL/test-evidence patch plan，并路由重验证 | `ARCH_REWRITE_PLAN`, `REWRITE_DECISION_REPORT`, `REGRESSION_TRACKING_REPORT` |

## 当前设计原则

系统的关键规则是单一真值、多阶段 lowering 和闭环修复：

- `SYSTEM_CONTRACT_IR` 是唯一 semantic truth source。
- `GOLDEN_CONTRACT_MODEL` 只能执行合同语义，不能重新定义 ISA、memory、launch、scheduler 或 config truth。
- RTL 不是一次性全局生成，而是通过 `INCREMENTAL_RTL_MAP` 做 module-by-module binding。
- 性能报告必须升级为 `PERF_ATTRIBUTION_GRAPH`，连接 cycle、warp、memory、contract path 和 RTL module evidence。
- closure 不再只是 report，而是由 rewrite controller 输出 `ARCH_REWRITE_PLAN` 并触发 revalidation。

## 保留资产

`shared/` 现在只保留 v5 必需资产：

- `shared/schemas/`：v5 IR 和 report schema。
- `shared/tables/`：v5 决策表、taxonomy、binding table、routing table。
- `shared/tests/`：五个核心 skill 的 regression cases 和资产 validator。
- `shared/examples/self_correcting_minimal_simt/`：当前唯一保留的闭环示例。
- `shared/references/`：Vortex、MIAOW、GPGPU-Sim、Rocket、XiangShan、Vibe-GPU lessons。
- `shared/flow/`：当前五模块设计流说明。

## 文件说明索引

每个子文件的中文说明都集中写在 `file_descriptions.zh.md`。该文件对每个 Markdown、YAML 和 Python 文件都给出：

- 内容说明：这个文件装了什么、负责什么。
- 具体例子：这个文件在实际 GPGPU skill flow 中怎么被使用。

如果新增、删除或移动文件，需要同步更新 `file_descriptions.zh.md`，否则 validator 会失败。

## 旧 skill 迁移状态

旧顶层 skills 和旧 `legacy/` skills 不再保留为可调用入口。它们有用的约束已经迁移到当前五个 skill 的核心约束文件中：

| 旧来源 | 当前承接位置 |
|---|---|
| front-end / architecture synthesizer / mode controller / design intent lock | `gpgpu-architecture-generator/legacy_request_and_candidate_constraints.md` |
| spec lock / canonical state / config truth / golden sim truth | `gpgpu-system-contract-golden-engine/contract_truth_and_state_model.md` |
| artifact contract / memory path structure / deterministic transform / RTL module gates | `gpgpu-incremental-rtl-binding-engine/module_binding_rules.md` |
| runtime validator / memory validation / implementation validator / causal trace analyzer | `gpgpu-simulation-performance-attribution-engine/legacy_validation_and_trace_constraints.md` |
| closure refinement / synthesis closure / repair routing | `gpgpu-architecture-rewrite-loop-controller/legacy_closure_repair_constraints.md` |

## 验证方式

当前主校验命令是：

```bash
python3 shared/tests/validate_v4_assets.py
```

该脚本会检查：

- 五个核心 GPGPU skill 是否存在且包含必要章节。
- 旧顶层 skill、旧 `legacy/`、旧 `examples/`、旧 `references/` 和旧 v4 generator 是否回流。
- `shared/` 是否只保留 v5 允许的 schemas、tables、tests、examples、references 和 flow。
- 所有文件是否都在 `file_descriptions.zh.md` 中有中文内容说明和具体例子。
