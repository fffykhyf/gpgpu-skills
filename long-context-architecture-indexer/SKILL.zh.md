---
name: long-context-architecture-indexer
description: 当 GPT-5.5 等规划 agent 委派只读长上下文分析时使用，适用于大型 PDF、论文、spec、manual、仓库、RTL、simulator、测试、日志或长源码。按 document 或 repository 模式输出标准 evidence package，调用方只指定 mode、focus、depth 和 questions。
---

# 长上下文架构索引器

## 概览

这个 skill 是 `arch_reader` 类 agent 的工作流层：它把大文档或大代码库压缩成稳定、可追溯、可被 GPT-5.5 继续消费的 evidence package。

模型、sandbox、工具权限和 context window 属于 agent runtime 配置；这个 skill 只定义读法、证据纪律和标准输出协议。

## 职责边界

- 默认只读源码仓库、PDF 和长文档，除非规划 agent 明确要求写报告产物。
- 不实现代码、不写 patch、不重构、不做最终架构决策。
- 输出结构化 evidence package，不做自由发挥式总结。
- 区分事实、解释和不确定项：`CONFIRMED`、`INFERRED`、`UNCERTAIN`。
- 尽量引用精确证据：文件路径、符号、函数、模块、行号范围、PDF 页码、章节、URL 或 commit hash。
- 明确报告已读内容、跳过内容、缺失上下文、证据冲突和置信度限制。
- 每个报告末尾必须给 GPT-5.5 一个紧凑 handoff。

## 规划 Agent 输入

GPT-5.5 调用时只需要指定这些变量：

```yaml
mode: "document"        # document | repository
focus:
  - "Architecture contracts relevant to simple-gpgpu"
depth: "normal"         # scan | normal | deep
questions:
  - "Which assumptions are reusable?"
  - "Which assumptions should not be copied?"
corpus:
  - path: "ref_submodule/vortex"
write_to: "docs/agent-output/repo-reports/2026-06-22-vortex-simt.md"
```

不要让 GPT-5.5 每次重写输出模板。如果规划 agent 提供额外 section，只能作为附加项，不能替代标准证据包的必要部分。

## 两个模式

| Mode | 适用材料 | 必须使用的模板 |
|---|---|---|
| `document` | PDF、论文、spec、manual、book、长 Markdown、架构报告 | 输出前读取 `references/document-mode-template.md`。 |
| `repository` | 仓库、子模块、RTL、simulator、测试、日志、长实现代码 | 输出前读取 `references/repository-mode-template.md`。 |

如果调用方没给 `mode`，根据材料类型推断，并在 Metadata 中说明假设。

## 深度

| Depth | 目标长度 | 规则 |
|---|---:|---|
| `scan` | 1K-3K words | 高层地图、关键证据、主要风险和下一步文件/章节。用于判断材料是否相关。 |
| `normal` | 3K-8K words | 完整标准模板，表格保持紧凑。用于常规 evidence package。 |
| `deep` | 8K-20K words | 完整模板、证据索引、矛盾、缺失 contract、详细 next actions。用于 GPT-5.5 做架构决策前。 |

如果没给 `depth`，默认 `normal`。

## 工作流

1. **接收任务**：复述 mode、depth、corpus、focus、questions、write target 和 non-goals。
2. **材料盘点**：识别材料类型、版本、入口点、文件数量、主要目录、文档章节和 source-of-truth。
3. **加载模板**：读取对应 mode 的 `references/` 模板。
4. **制定阅读顺序**：先读 manifest、AGENTS.md、README、论文、spec、docs、构建文件、顶层模块和测试，再深读实现。
5. **架构扫描**：提取模块、owner、接口、状态、数据流、控制流、配置点、测试、评估钩子和证据。
6. **聚焦深读**：只围绕 focus 和 questions 深读。
7. **证据绑定**：每个会影响规划的 claim 都绑定来源。
8. **交接输出**：按标准报告模板输出，并以 GPT-5.5 next actions 收尾。

## GPGPU / RTL 固定检查项

当 `mode: repository` 且目标是 GPGPU、RTL、simulator 或架构代码时，即使 focus 只提到一部分，也要检查：

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

没有找到的主题要写入 Missing Contracts 或 Open Questions，不能静默跳过。

## 报告路径

需要写产物时，默认使用：

- `docs/agent-output/document-reports/YYYY-MM-DD-<topic>.md`
- `docs/agent-output/repo-reports/YYYY-MM-DD-<topic>.md`

如果规划 agent 提供 `write_to`，按它指定的位置写。
