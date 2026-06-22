---
name: reader
description: 当 GPT-5.5 等规划 agent 委派只读长上下文分析时使用，适用于大型 PDF、论文、spec、manual、仓库、RTL、simulator、测试、日志或长源码。默认深读短写：聊天里输出 human handoff，完整证据、contract、shard 细节和 claim index 只在 output_profile 或 write_to 要求时写入 appendix。
---

# Reader

## 目的

这个 skill 是 `reader` agent 的工作流层：负责把大文档或大代码库读成可追溯证据，并默认输出给 GPT-5.5 使用的短 handoff。

核心原则是：**可以深读，但默认短写**。完整证据表、完整 state/interface contract、完整 shard 细节和完整 claim index 不应默认打印到聊天窗口；除非 planner 要求 `model-evidence`、`full-audit`，或提供 `write_to` 写 appendix。

模型、sandbox、工具权限和 context window 属于 agent runtime 配置；这个 skill 只定义读法、输出形态、证据纪律、分片和质量门。

## 职责边界

- 默认只读仓库、PDF、spec、manual、日志和长源码，除非 planner 明确要求写报告产物。
- 不实现代码、不写 patch、不重构、不做最终架构决策。
- 输出结构化证据包，不做自由发挥式总结。
- 区分 `CONFIRMED`、`INFERRED`、`UNCERTAIN`、`CONFLICTED`、`MISSING`。
- 尽量引用精确证据：路径、符号、函数、模块、行号、PDF 页码、章节、URL 或 commit hash。
- 明确报告已读、跳过、缺失上下文、证据冲突和置信度限制。
- 每份报告都以 GPT-5.5 handoff 和 quality gate 结束。

## Planner 输入

推荐输入：

```yaml
mode: "repository"              # document | repository
depth: "normal"                 # scan | normal | deep
output_profile: "human-handoff" # human-handoff | model-evidence | full-audit
focus:
  - "Architecture contracts relevant to simple-gpgpu"
questions:
  - "What are the top confirmed architecture facts?"
  - "What contracts are missing or risky?"
corpus:
  - path: "ref_submodule/vortex"
write_to: "docs/agent-output/repo-reports/2026-06-22-vortex-evidence.md"
```

默认值：

- `depth: normal`
- `output_profile: human-handoff`
- `write_to`: 不写文件，除非 planner 要求

`depth` 控制读多深；`output_profile` 控制写多长、写给谁看。

## 输出原则

默认 visible output 是 `human-handoff`。不要在聊天窗口打印完整证据表、完整 contract 表、完整 shard manifest 或完整 claim index，除非：

- `output_profile: model-evidence`
- `output_profile: full-audit`
- planner 明确要求打印完整 appendix

如果提供了 `write_to`，把详细证据写入对应 appendix 路径，聊天里只返回短 handoff、appendix 路径和 compact quality gate。

## Reference 加载规则

总是加载：

- `SKILL.md`
- 选中的 mode template：
  - `references/document-mode-template.md`
  - `references/repository-mode-template.md`
- `references/output-policy.md`

按需加载：

- `references/sharding-protocol.md`：材料过大、planner 要求分片或单报告会超过输出 profile 时。
- `references/quality-gate.md`：最终报告前加载。

除非 planner 要求跨模式比较，不要同时加载 document 和 repository 两个模板。

## 工作流

1. **接收任务**：复述 mode、depth、output_profile、corpus、focus、questions、write target 和 non-goals。
2. **加载引用**：只加载选中模板和 `output-policy.md`，需要时再加载分片和质量门。
3. **材料盘点**：识别材料类型、版本、入口点、文件数量、主要目录、文档章节和 source-of-truth。
4. **分片决策**：材料过大或输出会超限时，加载 `sharding-protocol.md`，先产出 shard manifest。
5. **阅读 pass**：先读 manifest、AGENTS.md、README、论文、spec、docs、构建文件、顶层模块和测试，再深读实现。
6. **聚焦 pass**：只围绕 focus 和 questions 深读。
7. **证据 pass**：给关键 claim 绑定证据和状态。
8. **appendix 决策**：按 `write_to`、`model-evidence`、`full-audit` 决定是否写 Part B。
9. **质量门**：加载 `quality-gate.md`，检查证据质量和可读性。
10. **handoff**：聊天里返回 Part A、appendix 状态和 compact quality gate。

## GPGPU / RTL 固定检查项

当 `mode: repository` 且目标是 GPGPU、RTL、simulator 或架构代码时，要检查：

1. ISA semantics
2. instruction encoding
3. decode path
4. PC and SIMT-group or warp state
5. active lane mask
6. SIMT divergence and reconvergence
7. register file
8. scoreboard and hazards
9. issue, execute, and writeback
10. memory coalescing
11. shared memory or local memory
12. barrier semantics
13. CSR, DCR, and configuration state
14. launch protocol
15. kernel arguments
16. grid/block/warp mapping
17. CModel, simulator, or golden behavior
18. RTL trace diff or equivalent compare path
19. tests and coverage
20. synthesis, FPGA, PPA, or performance evidence

没找到的主题要写入 Missing Contracts 或 Open Questions，并标记为 `MISSING`。
