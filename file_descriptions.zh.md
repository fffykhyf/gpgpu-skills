# Skill 文件中文说明索引

## 覆盖规则

本文件覆盖 `skill/` 仓库中除 `.git/` 以外的每一个子文件。每个条目都说明该文件放了什么内容、它在 GPGPU skill 体系中的作用，并给出一个具体例子，方便后续维护者快速判断文件是否还能删除、迁移或扩展。

### `README.md`

内容说明：这是 `skill/` 仓库的入口说明，概括 self-correcting GPGPU design system 的目标、六个顶层 skill、核心输出、legacy 迁移原则和 shared 资产边界。它告诉读者当前仓库已经不是旧 9-stage pipeline，而是以可执行合同、toolchain artifact、增量 RTL、因果归因和 rewrite loop 为核心的 v5 skill 系统。

具体例子：新维护者打开仓库时，可以先读这里确认当前只应调用 `gpgpu-architecture-generator`、`gpgpu-system-contract-golden-engine`、`gpgpu-toolchain-runtime-artifact-engine`、`gpgpu-incremental-rtl-binding-engine`、`gpgpu-simulation-performance-attribution-engine`、`gpgpu-architecture-rewrite-loop-controller` 六个 GPGPU skill。

### `file_descriptions.zh.md`

内容说明：本文件是全仓库子文件的中文说明索引，逐项解释每个 Markdown、YAML 和 Python 文件的内容、用途与具体例子。它不是运行时输入，而是维护文档，帮助判断文件职责是否重复、是否仍被当前 v5 skill 使用。

具体例子：如果有人想删除 `shared/tables/rewrite_trigger_table.yaml`，可以先查本文件对应条目，确认它定义 root cause 到 patch type 的触发关系，删除会影响 rewrite controller 的决策依据。

### `gpgpu-architecture-generator/SKILL.md`

内容说明：这是 Architecture Generator 的主 skill 文件，定义它如何把用户请求、可选 spec、trace 或 patch request 转成 `MODE_SELECTION_IR`、`DESIGN_INTENT_IR`、候选 `ARCH_IR` 和 `MICRO_CONSTRAINT_ESTIMATE_IR`。文件还规定它不能冻结系统语义、不能生成 RTL、不能产生 rewrite plan。

具体例子：用户说“从零设计一个教学用 SIMT GPGPU”，该 skill 负责锁定目标、选择 preset、估计面积和 memory pressure，并输出候选架构图，而不是直接定义 ISA ordering 或 RTL pipeline。

### `gpgpu-architecture-generator/legacy_request_and_candidate_constraints.md`

内容说明：该文件迁移旧 front-end、architecture synthesizer、mode controller 和 design-intent-lock 中仍有价值的请求分类、intent lock 和 candidate graph 约束。它明确旧逻辑只作为新 Architecture Generator 的约束来源，不再作为独立 skill 存在。

具体例子：当用户只说“做个高性能 GPU”但没有 workload、platform 和 validation target 时，这个文件要求输出 `INSUFFICIENT_REQUEST` 或显式 non-goal，而不能偷偷推断 warp size 或 cache policy。

### `gpgpu-architecture-rewrite-loop-controller/SKILL.md`

内容说明：这是 Architecture Rewrite Loop Controller 的主 skill 文件，定义它如何消费 `PERF_ATTRIBUTION_GRAPH`、`ROOT_CAUSE_REPORT`、`PASS_EVIDENCE_REPORT`、`ARCH_IR`、`SYSTEM_CONTRACT_IR`、toolchain artifacts 和 `INCREMENTAL_RTL_MAP`，并生成 `ARCH_REWRITE_PLAN`、`REWRITE_DECISION_REPORT` 与 `REGRESSION_TRACKING_REPORT`。它强调 controller 只能提出 patch plan，不能直接修改 IR。

具体例子：如果 perf graph 显示 shared memory bank conflict 导致大量 warp stall，该 skill 可以输出 RTL Patch 或 Architecture Patch；如果 pass evidence 缺少 coverage 或 fingerprint，则输出 Pass Evidence Patch 而不是误判设计错误。

### `gpgpu-architecture-rewrite-loop-controller/legacy_closure_repair_constraints.md`

内容说明：该文件迁移旧 closure refinement 和 synthesis closure 的 gate、repair routing、failure attribution 规则。它把旧的 `ACCEPT`、`REJECT`、`REFINE_REQUIRED`、`INSUFFICIENT_EVIDENCE` 映射到 v5 rewrite decision 语义。

具体例子：旧系统中的 `MEMORY_DUMP_CONTRACT_MISMATCH` 现在会成为 rewrite controller 的故障标签，并被映射到 RTL Patch 或 Test Evidence Patch，而不是重新启用旧 closure skill。

### `gpgpu-architecture-rewrite-loop-controller/patch_taxonomy.md`

内容说明：该文件定义 rewrite plan 可使用的 patch 类型，包括 Architecture Patch、Contract Patch、Golden Model Patch、Toolchain Patch、Runtime Patch、RTL Patch、Pass Evidence Patch 和 Test Evidence Patch。它让 controller 对“该改架构、合同、golden、工具链、runtime、RTL 还是证据”有稳定分类。

具体例子：如果 root cause 是 `RUNTIME_LAUNCH_ROOT_CAUSE/ARG_BUFFER_ENCODING_MISMATCH`，应归类为 Runtime Patch；如果是 `TEST_EVIDENCE_ROOT_CAUSE/INSUFFICIENT_COVERAGE`，应归类为 Pass Evidence Patch 或 Test Evidence Patch。

### `gpgpu-architecture-rewrite-loop-controller/regression_tracking.md`

内容说明：该文件说明 rewrite loop 必须如何记录 regression risk、历史失败、已应用 patch 和后续验证结果。它避免系统只修当前失败，却忘记历史通过的行为。

具体例子：一次把 warp size 从 8 改到 16 的 Architecture Patch，必须记录可能影响 active mask、register pressure 和 occupancy 的 regression risk。

### `gpgpu-architecture-rewrite-loop-controller/revalidation_routing.md`

内容说明：该文件定义不同 patch 类型需要重新路由到哪些模块和 gate。它把 rewrite plan 和后续验证连接起来，避免 patch 只停留在建议文本。

具体例子：Runtime Patch 应重跑 runtime arg encoding、CSR launch sequence、completion/fault observation 和 RTL/golden trace diff；Pass Evidence Patch 应重跑 pass evidence report、coverage check、performance metric 和 regression fingerprint。

### `gpgpu-architecture-rewrite-loop-controller/rewrite_trigger.md`

内容说明：该文件描述 root cause 如何触发 rewrite。它使用新的两级 root cause taxonomy，把 toolchain、runtime launch、RTL functional/interface、memory、scheduler、performance architecture 和 test evidence root cause 映射到对应 patch type，并规定证据足够、owner 明确、revalidation route 存在时才能产生 rewrite plan。

具体例子：`PERFORMANCE_ARCH_ROOT_CAUSE` 可以触发 Architecture Patch；`PASS_EVIDENCE_REPORT` 显示 coverage 或 fingerprint 证据不足时，只能触发 Pass Evidence Patch 或 Test Evidence Patch。

### `gpgpu-incremental-rtl-binding-engine/SKILL.md`

内容说明：这是 Incremental RTL Binding Engine 的主 skill 文件，定义它如何把 `SYSTEM_CONTRACT_IR` 和 `GOLDEN_CONTRACT_MODEL` 逐模块绑定成 `INCREMENTAL_RTL_MAP`。它强调 module-by-module assembly、interface contract checking 和 RTL partial simulation。

具体例子：在实现 load/store queue 时，该 skill 要求声明 consumed contract paths、provided signals、latency contract、local trace schema，并用 golden slice 做局部仿真对比。

### `gpgpu-incremental-rtl-binding-engine/interface_binding_and_checker.md`

内容说明：该文件定义结构化 `INTERFACE_BINDING_IR`，并说明接口合同检查器要检查 payload 字段、握手协议、tag ordering、latency、reset、trace tap、adapter 和 no combinational ready loop。它是防止模块拼接后才暴露接口错误的约束文档。

具体例子：如果 LSQ 到 coalescer 的 `REQ_RSP_TAGGED` interface 在 response 前复用 tag，checker 必须报告 `TAG_REUSE_BEFORE_RESPONSE`；如果 ready 形成组合环，必须报告 `COMBINATIONAL_READY_LOOP`。

### `gpgpu-incremental-rtl-binding-engine/module_binding_rules.md`

内容说明：该文件定义 deterministic module binding、`MODULE_BINDING_TEMPLATE` 要求、memory path structural rules、timing/synthesis feedback hook 和 fail-closed 规则。它把旧 artifact-contract、memory-subsystem、runtime interface 和 RTL SIMT core 中有价值的绑定规则归并到当前增量 RTL 绑定层。

具体例子：`load_store_queue` module 必须引用 `lsq_template`，声明 consumed contract paths、required local state、input/output interfaces、partial sim cases、timing feedback，并证明没有 combinational ready loop。

### `gpgpu-incremental-rtl-binding-engine/partial_simulation_gates.md`

内容说明：该文件定义每个 RTL module 进入 full-system simulation 前必须通过的 partial simulation gate，包括 required inputs、required outputs、模块级具体用例和失败证据格式。

具体例子：scoreboard partial sim 必须覆盖 RAW dependency stall、writeback wakeup 和 multiple warp independence；LSQ partial sim 必须覆盖 ready-low payload stability、tag unique、response wakeup 和 fault propagation。

### `gpgpu-incremental-rtl-binding-engine/rtl_module_catalog.md`

内容说明：该文件列出 v5 RTL binding 需要考虑的模块目录和 memory path 分解，例如 SM core、warp scheduler、execute pipeline、register file、scoreboard、SIMT stack、LSQ、coalescer、shared memory bank unit、L1/global adapter、memory response router、fault/completion unit 和 CSR runtime interface。

具体例子：memory path 不应只建一个 cache/global interface，而应拆出 `coalescer`、`l1_cache_or_global_adapter`、`memory_response_router` 和 `fault_completion_unit`，除非模板显式允许融合并保留检查证据。

### `gpgpu-simulation-performance-attribution-engine/SKILL.md`

内容说明：这是 Simulation Evidence and Performance Attribution Engine 的主 skill 文件，定义如何归一化 runtime、memory、RTL、waveform、module partial sim、golden 和 toolchain trace，先生成 `CORRECTNESS_GATE_REPORT`，再进入 failure attribution 或 pass evidence mode。它要求通过时也生成 `PASS_EVIDENCE_REPORT`、coverage、performance metrics 和 regression fingerprint。

具体例子：当 RTL final memory 与 golden 一致时，该 skill 不能直接跳过，而要输出 pass evidence、trace coverage、IPC/stall 指标和 `REGRESSION_FINGERPRINT`；当不一致时才进入 first divergence 和 root cause 定位。

### `gpgpu-simulation-performance-attribution-engine/bottleneck_graph_builder.md`

内容说明：该文件说明如何把 normalized event 和 performance metric 构造成 bottleneck graph。它从 memory-centric 链路扩展为 template-driven graph，覆盖 memory latency、shared bank conflict、scheduler underutilization、barrier、branch divergence、pipeline imbalance、interface backpressure、toolchain mismatch 和 runtime launch mismatch。

具体例子：scheduler underutilization graph 可以把 low eligible warp count 连接到 scoreboard/barrier/divergence，再映射到 warp scheduler module 和 scheduler contract path。

### `gpgpu-simulation-performance-attribution-engine/correctness_gate_and_mode_selection.md`

内容说明：该文件定义 correctness gate 的输入、输出和模式选择规则，用 final memory、architectural state、completion/fault status、trace-level divergence 和 evidence completeness 决定进入 `FAILURE_ATTRIBUTION_MODE` 还是 `PASS_EVIDENCE_MODE`。

具体例子：如果 final memory 一致但 instruction trace 出现 active mask divergence，该 gate 要选择 failure attribution mode 并要求 first divergence report；如果结果一致但缺少 RTL trace，则输出 `PASS_WITH_INSUFFICIENT_EVIDENCE`。

### `gpgpu-simulation-performance-attribution-engine/differential_correctness_engine.md`

内容说明：该文件定义 failure mode 下的 RTL/golden 差分比较规则，包括 PC、next PC、decode、active mask、predicate、register writeback、memory request/response、CSR、barrier、fault 和 completion。它要求选择第一个 deterministic architectural divergence。

具体例子：final memory mismatch 只能作为 symptom；如果更早的证据显示 entry PC 错，`FIRST_DIVERGENCE_REPORT` 应指向 PC mismatch，而不是把 memory dump mismatch 当根因。

### `gpgpu-simulation-performance-attribution-engine/legacy_validation_and_trace_constraints.md`

内容说明：该文件迁移旧 runtime validator、memory validation、implementation validator、golden sim 和 causal trace analyzer 中仍有价值的验证规则，并把旧的 “RTL == golden 即结束” 降级为兼容行为。v5 中 pass 也必须生成 pass evidence、coverage、performance metrics 和 fingerprint。

具体例子：旧 `APP_COMPILE_FAIL` 不再由 runtime-validator 独立处理，而是作为 Test Evidence 或 root cause 输入；通过用例也必须留下 `PASS_EVIDENCE_REPORT`，否则只能算 `PASS_WITH_INSUFFICIENT_EVIDENCE`。

### `gpgpu-simulation-performance-attribution-engine/minimal_trace_window_rules.md`

内容说明：该文件定义 minimal trace window 的选择规则，区分 correctness window 和 performance window。Correctness window 围绕 first divergence 包含 last matching event、first mismatching event 和 dependency closure；performance window 选择 stall contribution 最大且证据最完整的连续窗口。

具体例子：寄存器写回第 42 cycle 首次不一致时，窗口默认包含前后各 8 个相关事件、依赖事件、contract path、RTL module path 和可能的 toolchain artifact path。

### `gpgpu-simulation-performance-attribution-engine/pass_evidence_engine.md`

内容说明：该文件定义 pass mode 的证据报告规则，要求输出 `PASS_EVIDENCE_REPORT`、`TRACE_COVERAGE_REPORT` 和 `REGRESSION_FINGERPRINT`。它检查 evidence completeness、architectural state comparison、coverage、performance metric ref 和 warning。

具体例子：vector add 通过时，报告需要记录 system contract hash、golden model hash、RTL hash、program image hash、input/final memory hash、coverage hash 和 performance metric hash。

### `gpgpu-simulation-performance-attribution-engine/performance_metric_extractor.md`

内容说明：该文件定义 `PERFORMANCE_METRIC_IR` 的指标层级和字段，包括 total cycles、IPC、issue utilization、pipeline utilization、stall breakdown、memory metrics、scheduler metrics 和 warning flags。

具体例子：如果 correctness pass 但 memory_wait 占比过高，该 extractor 会输出 `HIGH_MEMORY_STALL`，performance gate 可以进一步要求构建 bottleneck graph。

### `gpgpu-simulation-performance-attribution-engine/report_generation_rules.md`

内容说明：该文件定义统一 `SIM_PERF_ATTRIBUTION_REPORT` 的组装规则，把 correctness gate、first divergence 或 pass evidence、performance metrics、toolchain attribution、coverage、root cause、top bottleneck 和 rewrite handoff 串成最终报告。

具体例子：failure mode 报告必须引用 `FIRST_DIVERGENCE_REPORT` 和 `ROOT_CAUSE_REPORT`；pass mode 报告必须引用 `PASS_EVIDENCE_REPORT`、coverage、metric 和 fingerprint。

### `gpgpu-simulation-performance-attribution-engine/root_cause_engine.md`

内容说明：该文件定义两级 root cause taxonomy 和 rewrite handoff 字段，覆盖 contract、golden、toolchain、runtime launch、RTL functional、RTL interface、memory system、scheduler、performance architecture、test evidence、insufficient trace 和 ambiguous cause。

具体例子：assembler 编码错应输出 `TOOLCHAIN_ROOT_CAUSE/ASM_ENCODE_MISMATCH` 并路由到 `gpgpu-toolchain-runtime-artifact-engine`；active mask 错应输出 `RTL_FUNCTIONAL_ROOT_CAUSE/ACTIVE_MASK_MISMATCH` 并路由 RTL revalidation。

### `gpgpu-simulation-performance-attribution-engine/toolchain_trace_attribution.md`

内容说明：该文件定义 assembly、encoded bytes、disassembly、program image、loader、runtime launch 到 RTL fetch/decode 的归因链。它用于区分 assembler 编码错、disassembler roundtrip 错、program image layout 错、entry PC 错、loader/runtime 错、RTL fetch/decode 错和 golden decode 错。

具体例子：如果 RTL fetch 到的 instruction 与 golden 不一致，必须先比较 assembler output hash、program image hash、loader contract hash 和 runtime launch hash，再决定是 toolchain root cause 还是 RTL fetch/decode root cause。

### `gpgpu-simulation-performance-attribution-engine/trace_ingestion_and_normalization.md`

内容说明：该文件替代旧 trace normalizer，定义多来源 trace ingestion、字段归一化、时间基准统一、event dictionary、contract path/RTL module/toolchain artifact 映射、trace hash 和 missing field 检查。

具体例子：RTL 里的 `pc_q`、golden trace 里的 `warp.pc`、waveform dump 里的 `u_fetch.pc` 和 toolchain first-fetch evidence 都要归一化到统一的 `pc` / `instruction_id` / `event_source` 字段。

### `gpgpu-system-contract-golden-engine/SKILL.md`

内容说明：这是 System Contract + Golden Semantics Engine 的主 skill 文件，定义它如何把 `ARCH_IR` 冻结为唯一 truth source `SYSTEM_CONTRACT_IR`，并派生可执行 reference semantics `GOLDEN_CONTRACT_MODEL`。它是 v5 系统唯一的语义冻结层。

具体例子：当 `ARCH_IR` 选择 `ROUND_ROBIN` scheduler 时，该 skill 要把调度规则写进 `SYSTEM_CONTRACT_IR`，再生成可执行的 scheduler reference function。

### `gpgpu-system-contract-golden-engine/contract_truth_and_state_model.md`

内容说明：该文件定义 `SYSTEM_CONTRACT_IR` 的唯一 truth ownership、contract freeze algorithm、结构化 canonical state model、source-of-truth map、config class semantics、artifact truth hygiene 和系统级 interface semantics model。

具体例子：`state_model` 必须显式包含 `pc_table`、`exec_mask_table`、`scoreboard_state`、`pipeline_visible_state`、`memory_stall_state` 等字段；`interface_semantics_model` 必须定义 accepted request 是否 eventually response、payload 是否 stable、tag 是否 unique until response。

### `gpgpu-system-contract-golden-engine/executable_semantics_rules.md`

内容说明：该文件合并 execution、memory、launch、config 和 interface semantics 规则，统一描述 semantics function record format、feature-gated required functions 和 fail-closed rules。

具体例子：当 `memory_model.atomic.enabled = false` 时，golden model 应实现 `reject_atomic_or_trap` 并记录 unsupported reason；只有 atomic feature 开启时才要求 `atomic_apply`。

### `gpgpu-system-contract-golden-engine/golden_model_coverage_and_report.md`

内容说明：该文件定义 `GOLDEN_CONTRACT_MODEL` 的边界、禁止 independent truth 的检查、contract path coverage、feature-gated coverage、报告字段和失败模式。

具体例子：`simt_divergence` 关闭时 coverage 不要求 `resolve_divergence`；`visible_pipeline_commit` 开启时 coverage 必须包含 `commit_pipeline_visible_state`。

### `reader/SKILL.md`

内容说明：这是 reader skill 的英文主说明，负责把文档或仓库读取任务结构化，要求按 mode、scope、sharding、quality gate 输出可追踪阅读结果。它不是 GPGPU 生成闭环的一环，而是证据读取辅助 skill。

具体例子：当需要读取一个参考仓库来提取 GPU memory path lesson 时，reader 可以分片读取文件并输出带证据锚点的摘要。

### `reader/SKILL.zh.md`

内容说明：这是 reader skill 的中文版本说明，面向中文使用场景解释如何读取长文档、仓库或资料并输出结构化证据。它与英文版职责一致，但便于中文维护者直接使用。

具体例子：维护者要分析一份中文设计文档时，可以用该文件描述的流程提取章节、约束、证据和未决问题。

### `reader/agents/openai.yaml`

内容说明：该 YAML 文件是 reader skill 的 agent 配置，声明 OpenAI agent 使用该 skill 时的简要说明和入口。它是工具/agent 发现层的配置资产，不承载 GPGPU IR 语义。

具体例子：如果一个 agent marketplace 或 runner 读取 skill 配置，它可以从这里知道 reader 的定位和可调用元信息。

### `reader/references/document-mode-template.md`

内容说明：该模板定义 reader 在 document mode 下如何组织输出，包括文档范围、章节结构、关键事实、引用证据和风险。它用于读取单份文档。

具体例子：读取一篇 GPU ISA 文档时，可以按该模板输出“指令编码事实”“未定义行为”“需要验证的引用行”。

### `reader/references/output-policy.md`

内容说明：该文件定义 reader 输出的质量规则，例如不要编造、需要标注证据、区分事实与推断、保持可追踪。它约束 reader 的输出可信度。

具体例子：如果资料里没有说明 memory ordering，reader 应输出“未找到证据”，而不是推断为 relaxed ordering。

### `reader/references/quality-gate.md`

内容说明：该文件定义 reader 的质量门槛，用来判断一次阅读结果是否足够完整、是否覆盖关键范围、是否保留证据路径。它用于结束阅读任务前的自检。

具体例子：读取仓库后，如果没有列出入口文件、核心模块和证据锚点，该 quality gate 应判定阅读结果不完整。

### `reader/references/repository-mode-template.md`

内容说明：该模板定义 reader 在 repository mode 下如何读取仓库，包括目录结构、关键文件、构建入口、测试入口、模块关系和风险点。它适合分析代码库。

具体例子：读取一个开源 GPGPU simulator 仓库时，可以按该模板记录 simulator core、memory model、trace 输出和测试用例位置。

### `reader/references/sharding-protocol.md`

内容说明：该文件定义长文档或大仓库的分片读取协议，说明如何拆分范围、避免遗漏、合并摘要并记录未读区域。它解决上下文长度不足时的阅读组织问题。

具体例子：分析一个包含 RTL、compiler、runtime 的大仓库时，可以按目录分 shard 分别读取，再合并成一份 evidence index。

### `shared/examples/self_correcting_minimal_simt/expected_arch_ir.yaml`

内容说明：该 YAML 是 self-correcting minimal SIMT 示例中期望的 `ARCH_IR` 输出，描述候选架构的拓扑、执行模型、存储层级和 provenance。它给 Architecture Generator 提供可回归的目标样例。

具体例子：测试 case 可以断言 minimal SIMT 设计的 `warp_size`、`sm_count` 和 `scheduler_policy` 与该文件一致。

### `shared/examples/self_correcting_minimal_simt/expected_arch_rewrite_plan.yaml`

内容说明：该 YAML 是示例中期望的 `ARCH_REWRITE_PLAN`，展示当系统发现瓶颈或错误时 rewrite controller 应给出的 patch 类型、owner、影响和 revalidation gates。

具体例子：如果 perf attribution 指向 memory imbalance，该文件可以展示一个增加 memory bandwidth 或调整 cache path 的 architecture patch。

### `shared/examples/self_correcting_minimal_simt/expected_golden_contract_model.yaml`

内容说明：该 YAML 是示例中期望的 `GOLDEN_CONTRACT_MODEL`，列出 contract-derived executable semantics 的函数、覆盖路径和禁止独立 truth 的约束。它验证 golden model 是合同派生物。

具体例子：`warp_schedule` 函数必须映射到 system contract 的 scheduler path，并携带 contract hash。

### `shared/examples/self_correcting_minimal_simt/expected_incremental_rtl_map.yaml`

内容说明：该 YAML 是示例中期望的 `INCREMENTAL_RTL_MAP`，描述模块目录、接口、latency contract、local trace 和 partial sim evidence。它验证 RTL 绑定是逐模块完成的。

具体例子：`warp_scheduler` module 条目会声明输入 scoreboard state、输出 selected warp、以及 local partial simulation evidence。

### `shared/examples/self_correcting_minimal_simt/expected_micro_constraint_estimate.yaml`

内容说明：该 YAML 是示例中期望的 `MICRO_CONSTRAINT_ESTIMATE_IR`，记录面积、memory pressure、occupancy、register pressure 和 bandwidth need 等可实现性估计。它用于防止不可实现架构太晚才暴露。

具体例子：对于 FPGA small target，它可以标注 shared memory pressure 或 bandwidth risk，提示候选架构需要收缩。

### `shared/examples/self_correcting_minimal_simt/expected_perf_attribution_graph.yaml`

内容说明：该 YAML 是示例中期望的 `PERF_ATTRIBUTION_GRAPH`，展示 cycle、warp、memory、contract path 和 RTL module path 如何连接成因果图。它验证性能报告必须有证据链。

具体例子：一个 node 可以表示 `warp_0_stall_cycle_18`，边连接到 `scoreboard_dependency` 和 `lsq_module_path`。

### `shared/examples/self_correcting_minimal_simt/expected_system_contract_ir.yaml`

内容说明：该 YAML 是示例中期望的 `SYSTEM_CONTRACT_IR`，冻结 execution model、state model、memory model、launch model 和 config contract。它是示例里的唯一 semantic truth。

具体例子：该文件可以声明 active mask width、PC state、global memory ordering 和 MMIO doorbell launch ABI。

### `shared/examples/self_correcting_minimal_simt/input_request.md`

内容说明：该 Markdown 是 self-correcting minimal SIMT 示例的输入请求，描述用户从零设计一个最小 SIMT GPGPU 时的目标、约束和验证诉求。它用于驱动端到端 regression。

具体例子：测试可以读取该请求，期望生成 minimal teaching GPU 的 `ARCH_IR`、`SYSTEM_CONTRACT_IR` 和 rewrite plan。

### `shared/flow/gpgpu_design_flow.md`

内容说明：该文件用中文/英文混合描述当前 v5 GPGPU design flow，从 Architecture Generator 到 Rewrite Loop Controller，并解释每个模块的输入输出和 fail-closed policy。它是系统级流程说明。

具体例子：当维护者不确定 memory model 应放在哪一层时，可以读这里确认 memory truth 在 System Contract，memory binding 在 Incremental RTL，memory correctness 在 Simulation Attribution。

### `shared/references/gpgpusim_lessons.yaml`

内容说明：该 YAML 记录从 GPGPU-Sim 借鉴的 lesson，主要强调 golden trace 是证据而不是 truth source。它作为参考经验输入，帮助避免 simulator 重定义合同语义。

具体例子：当 golden trace 与 RTL trace 不一致时，应回到 `SYSTEM_CONTRACT_IR` 判断真值，而不是让 simulator 自行决定 ISA 行为。

### `shared/references/miaow_lessons.yaml`

内容说明：该 YAML 记录从 MIAOW 借鉴的 SIMT core lesson，强调 lane mask 和 register behavior 必须在 validation trace 中可见。它服务 execution/state trace 的设计。

具体例子：设计 active mask trace schema 时，可以引用该 lesson 要求每个 divergence event 都能看到 lane mask 变化。

### `shared/references/reference_lesson_index.yaml`

内容说明：该 YAML 是 reference lessons 的索引文件，列出所有可用 lesson 文件。它让 validator 和读者知道 shared references 中哪些文件属于当前保留集。

具体例子：新增 `new_gpu_lessons.yaml` 时，应同时在该索引中登记，否则该 lesson 不会被统一发现。

### `shared/references/rocket_lessons.yaml`

内容说明：该 YAML 记录从 Rocket Chip 借鉴的配置所有权 lesson，强调 generator configuration 要有明确 owner 和 downstream consumer binding。它支持 config contract 和 RTL binding 的一致性。

具体例子：`warp_size` 是 hw/sw ABI 可见配置，必须由 System Contract 拥有，runtime 和 RTL 只能消费。

### `shared/references/vibe_gpu_lessons.yaml`

内容说明：该 YAML 记录 Vibe-GPU 相关 lesson，包括 vertical slice prototype 和 source-of-truth drift。它提醒 v5 系统必须有 end-to-end runnable evidence 和防漂移机制。

具体例子：如果 docs、RTL defines、assembler opcode table 不一致，该 lesson 要求以 `SYSTEM_CONTRACT_IR` 为唯一 truth。

### `shared/references/vortex_lessons.yaml`

内容说明：该 YAML 记录从 Vortex 借鉴的 warp scheduler lesson，强调 scheduler policy 必须以 contract 或显式 implementation policy 表达，不能让下游实现自行发明。

具体例子：如果采用 round-robin scheduler，contract 中必须定义选择顺序和 stalled warp 的处理规则。

### `shared/references/xiangshan_lessons.yaml`

内容说明：该 YAML 记录从 XiangShan 借鉴的 validation closure lesson，强调 pipeline 和 trace validation 要把失败路由到字段、规则和 owner。它支持 root cause attribution 和 rewrite routing。

具体例子：当 pipeline trace mismatch 出现时，应定位到 module path、contract path 和 failed gate，而不是只输出“RTL failed”。

### `shared/schemas/arch_generation_report_ir.schema.yaml`

内容说明：该 schema 定义 `ARCH_GENERATION_REPORT` 的结构，描述 Architecture Generator 的 verdict、输入 hash、候选架构 hash、约束风险和下游合同。它让架构生成报告可校验。

具体例子：一次架构生成后，报告必须包含 `selected_preset` 和 `known_unrealizable_risks` 字段。

### `shared/schemas/arch_ir.schema.yaml`

内容说明：该 schema 定义候选 `ARCH_IR` 的图结构，包括 candidate identity、结构化 `graph_nodes`、`graph_edges`、constraint proof 和 provenance。每个 graph node 必须显式给出 node type、owned state、input/output ports、required contract paths 和 scaling parameters，避免 RTL binding 阶段重新猜模块边界。

具体例子：`load_store_queue` node 应声明自己拥有 pending memory op state，输入 `memory_op`/`memory_response`，输出 `memory_request`/`lsq_backpressure`，并指向 `memory_model.request_lifecycle` 合同路径。

### `shared/schemas/arch_rewrite_plan.schema.yaml`

内容说明：该 schema 定义 `ARCH_REWRITE_PLAN`，包括 rewrite id、patch type、owner module、patch target、expected impact、required revalidation gates 和 regression risk。它约束 rewrite loop 的输出。

具体例子：一个 RTL Patch 计划必须包含目标模块如 `load_store_queue`，以及需要重跑的 `partial_sim` 和 trace attribution gate。

### `shared/schemas/contract_semantics_report_ir.schema.yaml`

内容说明：该 schema 定义 contract semantics report，用来记录 `SYSTEM_CONTRACT_IR` 到 `GOLDEN_CONTRACT_MODEL` 的覆盖、feature gate coverage、失败路径和禁止独立 truth 检查。它验证合同语义可执行。

具体例子：如果 atomic feature 关闭但 golden model 既没有 `reject_atomic_or_trap` 也没有 unsupported reason，报告应记录 feature gate coverage failure。

### `shared/schemas/design_intent_ir.schema.yaml`

内容说明：该 schema 定义 `DESIGN_INTENT_IR`，用于锁定用户目标、workload、target platform、validation target、non-goals 和 provenance。它只表达意图，不表达最终架构 truth。

具体例子：用户要求“教学用、可跑 vector add”，这里应记录 workload profile 和 validation target，而不是直接写死 cache policy。

### `shared/schemas/golden_contract_model.schema.yaml`

内容说明：该 schema 定义 `GOLDEN_CONTRACT_MODEL` 的结构，要求 execution、memory、launch、config 和 interface executable semantics function 映射到 contract path，并携带 contract hash、contract path coverage 和 feature gate coverage。它防止 golden model 变成第二套真值。

具体例子：`coalesce` 函数必须声明它来自 `SYSTEM_CONTRACT_IR.memory_model.coalescing`；`request_accept_lifecycle` 必须来自 `SYSTEM_CONTRACT_IR.interface_semantics_model.request_acceptance`。

### `shared/schemas/incremental_rtl_map.schema.yaml`

内容说明：该 schema 定义 `INCREMENTAL_RTL_MAP`，描述 module-by-module RTL binding 的模块、结构化 `INTERFACE_BINDING_IR`、module binding templates、latency contract、local trace schema、partial sim evidence 和 timing feedback。它替代旧的全局 RTL map。

具体例子：`scoreboard` module 条目必须声明 `scoreboard_template`、consumed contract paths、required local state、input/output interfaces、partial sim cases 和 `combinational_ready_loop_check`。

### `shared/schemas/micro_constraint_estimate_ir.schema.yaml`

内容说明：该 schema 定义 `MICRO_CONSTRAINT_ESTIMATE_IR`，记录 area、memory pressure、occupancy、register pressure、bandwidth need 和 risk assumptions。它用于早期发现不可实现架构。

具体例子：一个 candidate 如果 bandwidth_need 大于 target platform 上限，应在 `known_unrealizable_risks` 中列出。

### `shared/schemas/mode_selection_ir.schema.yaml`

内容说明：该 schema 定义 `MODE_SELECTION_IR`，记录请求属于 design、reproduce、patch request 还是 trace debug，以及下一步应进入哪个当前 v5 owner。它是请求入口的路由结构。

具体例子：用户提供 trace 和 divergence report 时，mode selection 应指向 Simulation Performance Attribution Engine。

### `shared/schemas/module_interface_report_ir.schema.yaml`

内容说明：该 schema 定义 module interface report，用于记录信号、握手、latency、pipeline boundary、payload stability、tag uniqueness 和 combinational ready loop 检查结果。它是 Incremental RTL Binding 的接口质量证据。

具体例子：如果 `req_ready` 参与组合环，report 应记录 `COMBINATIONAL_READY_LOOP`；如果 stalled payload 改变，应记录 `PAYLOAD_STABILITY_FAIL`。

### `shared/schemas/normalized_trace_ir.schema.yaml`

内容说明：该 schema 定义归一化 trace 的结构，统一 cycle、event type、warp id、contract path、RTL module path 和 evidence hash。它让不同来源 trace 可以比较。

具体例子：RTL waveform、golden trace 和 runtime trace 中的 PC event 都要归一化到同一种字段表示。

### `shared/schemas/perf_attribution_graph.schema.yaml`

内容说明：该 schema 定义 `PERF_ATTRIBUTION_GRAPH`，包含节点、边、证据、瓶颈类别和跨层路径。它要求性能结论必须连接 cycle、warp、memory、contract 和 RTL module。

具体例子：一个 cache miss bottleneck 节点必须连接到 memory request event 和 cache/global interface module。

### `shared/schemas/regression_tracking_report_ir.schema.yaml`

内容说明：该 schema 定义 regression tracking report，用于记录 rewrite 前后的风险、历史失败、重跑 gate 和是否引入回归。它让闭环优化有历史记忆。

具体例子：调整 scheduler policy 后，该 report 应记录 divergence、scoreboard 和 memory stall 相关 regression gates。

### `shared/schemas/rewrite_decision_report_ir.schema.yaml`

内容说明：该 schema 定义 rewrite decision report，记录 controller 为什么接受、拒绝或延后一个 patch plan。它把 root cause、证据和 patch taxonomy 连接起来。

具体例子：如果 trace evidence 不足，decision report 可以拒绝 Architecture Patch 并要求 Test Evidence Patch。

### `shared/schemas/root_cause_report_ir.schema.yaml`

内容说明：该 schema 定义 root cause report，记录故障类别、证据路径、affected contract path、RTL module path 和 ambiguity。它是 rewrite controller 的主要输入。

具体例子：`MEMORY_IMBALANCE` root cause 应包含 memory request evidence 和对应的 cache module path。

### `shared/schemas/rtl_partial_sim_report_ir.schema.yaml`

内容说明：该 schema 定义 RTL partial simulation report，记录单模块局部仿真输入、输出、golden slice 对比、模块级 case 结果和 timing feedback。它让 RTL module 在整机仿真前先过局部门槛。

具体例子：对 LSQ 模块，partial sim report 应包含 ready-low payload stable、tag unique、response wakeup、fault propagation 和 no combinational ready loop 的结果。

### `shared/schemas/sim_perf_attribution_report_ir.schema.yaml`

内容说明：该 schema 定义 Simulation Performance Attribution Engine 的总报告结构，汇总 normalized trace、perf graph、root cause、minimal trace window 和 evidence hashes。

具体例子：一次 RTL/golden mismatch 调试完成后，该 report 应指向 first divergence window 和 root cause report hash。

### `shared/schemas/system_contract_ir.schema.yaml`

内容说明：该 schema 定义 `SYSTEM_CONTRACT_IR`，也就是唯一语义真值层，覆盖 architecture model、`isa_model`、execution model、结构化 state model、memory model、launch model、interface semantics model 和 config contract。它是 Golden Semantics、RTL Binding 和 Verification 的共同基础。

具体例子：ISA opcode truth 应在 `isa_model.opcodes` 中冻结；request accepted 后是否 eventually response 应在 `interface_semantics_model.request_acceptance` 中冻结，而不是分散在 validator 或 RTL 文件中。

### `shared/tables/architecture_preset_library.yaml`

内容说明：该表定义 Architecture Generator 可选的架构 preset，以及确定性的 preset selection rules，例如 minimal SIMT、multi-warp single SM 和 vertical slice GPGPU。它为候选架构提供可追踪起点，并记录何时优先选择某个 preset。

具体例子：当 validation target 同时包含 program image 编译、RTL smoke test 和 memory dump golden check 时，generator 应优先选择 `MINIMAL_VERTICAL_SLICE_GPGPU`；只有教学且无 runtime/frontend 要求时才选择 `MINIMAL_SIMT_CORE`。

### `shared/tables/config_ownership_table.yaml`

内容说明：该表定义 config 字段的 owner、可见性和消费者，例如 `warp_size`、`trace_enable`、`block_dim` 等。它防止 runtime、RTL、simulator 随意修改配置真值。

具体例子：`warp_size` 由 System Contract Golden Engine 拥有，runtime 和 RTL 只能消费该字段。

### `shared/tables/contract_semantics_binding_table.yaml`

内容说明：该表把 `SYSTEM_CONTRACT_IR` 路径绑定到 executable semantics function，例如 scheduler、divergence、coalescing、ABI decode、atomic reject/trap 和 interface lifecycle。它确保每个可执行函数都有合同来源。

具体例子：`memory_model.atomic.unsupported_behavior` 可以绑定到 `reject_atomic_or_trap`；`interface_semantics_model.tag_uniqueness` 可以绑定到 `tag_uniqueness_until_response`。

### `shared/tables/enum_table.yaml`

内容说明：该表定义系统允许使用的枚举值，如 scheduler policy、cache policy、launch ABI、provenance 等。它阻止 hidden default 和 unknown enum 进入 IR。

具体例子：如果用户要求未登记的 warp scheduling policy，generator 或 contract engine 应拒绝而不是猜测。

### `shared/tables/golden_model_coverage_table.yaml`

内容说明：该表定义 golden model 必须覆盖的 contract semantics 路径、feature-gated coverage gate 和 forbidden independent truth gate。它用于判断 `GOLDEN_CONTRACT_MODEL` 是否完整执行合同。

具体例子：如果 `execution_model.features.simt_divergence` 关闭，则不强制要求 `resolve_divergence`；如果 `memory_model.atomic.enabled` 关闭，则要求 `reject_atomic_or_trap` 和 unsupported reason。

### `shared/tables/hard_constraint_table.yaml`

内容说明：该表定义 Architecture Generator 的硬约束，如 warp mask width、allowed enum、platform bound 等。它在 contract freeze 前筛掉不合法候选。

具体例子：请求 warp size 33 时，active mask width 约束会失败，generator 应输出 hard constraint failure。

### `shared/tables/micro_constraint_estimator_table.yaml`

内容说明：该表定义 micro-constraint estimator 使用的确定性估计规则，例如 area、memory pressure、occupancy 和 bandwidth bound。每个 estimator 应记录 inputs、output、formula/rule 和 failure mode，使同一组输入得到稳定的 feasibility estimate。

具体例子：area estimate 使用 register file、shared memory、cache 和 pipeline 的 relative area terms；如果 `max_warps_per_sm` 增加，register file area term 会按公式增加。

### `shared/tables/mode_decision_table.yaml`

内容说明：该表定义用户请求模式到当前 v5 skill owner 的路由规则，包括 complete spec、vague design、vertical slice、patch request 和 trace debug。它替代旧 mode controller。

具体例子：trace/debug 请求会路由到 Simulation Performance Attribution Engine，而不是旧 closure refinement skill。

### `shared/tables/module_interface_contract_table.yaml`

内容说明：该表定义 `INTERFACE_BINDING_IR` 的必需字段、protocol types、payload field、handshake、ordering、latency、reset、trace tap、adapter 和 checker failure modes。它为 Interface Contract Checker 提供检查依据。

具体例子：`REQ_RSP_TAGGED` interface 必须声明 tag 在 response 前唯一，payload stalled 时必须 stable，且不能形成 combinational ready loop。

### `shared/tables/patch_taxonomy_table.yaml`

内容说明：该表定义 patch taxonomy，把修复计划分为 Architecture、Contract、RTL 和 Test Evidence patch。它约束 rewrite controller 的输出分类。

具体例子：缺失 trace field 属于 Test Evidence Patch，而不是 Contract Patch。

### `shared/tables/perf_attribution_taxonomy.yaml`

内容说明：该表定义性能归因图中的瓶颈类别、节点类型和边类型。它让不同 trace case 的 bottleneck 归因保持一致。

具体例子：warp stall、cache miss、scoreboard wait 和 pipeline bubble 都可以作为规范化节点类别。

### `shared/tables/provenance_table.yaml`

内容说明：该表定义字段来源的合法 provenance，例如 user explicit、design preset、reference lesson、derived from contract 等。它防止模型猜测进入设计真值。

具体例子：`MODEL_GUESS` 或 `UNKNOWN` 作为 warp size 来源应被拒绝。

### `shared/tables/quality_target_table.yaml`

内容说明：该表定义架构生成时需要考虑的质量目标，如 throughput、area、memory bandwidth、prototype credibility 等。它让 candidate scoring 有明确目标。

具体例子：如果 target 是 FPGA prototype，quality target 应强调资源约束和可综合证据。

### `shared/tables/requirement_owner_table.yaml`

内容说明：该表定义不同 requirement 的当前 v5 owner，例如 SIMT execution、launch ABI、canonical state、RTL trace、closure verdict 等。它避免多个模块争夺同一 truth。

具体例子：`memory_ordering` 的 owner 是 System Contract Golden Engine，而不是 memory validator。

### `shared/tables/revalidation_routing_table.yaml`

内容说明：该表定义不同 patch 后必须重新运行哪些模块和验证 gate。它让 rewrite plan 进入可执行闭环。

具体例子：Contract Patch 需要重新运行 Golden Semantics、Incremental RTL Binding 和 Simulation Attribution。

### `shared/tables/rewrite_trigger_table.yaml`

内容说明：该表定义 root cause 到 rewrite trigger 的映射，决定哪些失败可以触发 architecture、contract、RTL 或 test-evidence patch。它是 rewrite controller 的触发表。

具体例子：`ROOT_CAUSE_AMBIGUOUS` 不应直接触发架构修改，而应触发补充证据。

### `shared/tables/root_cause_taxonomy.yaml`

内容说明：该表定义 root cause 类别和每类需要的证据，例如 contract violation、RTL structural issue、memory imbalance、scheduling inefficiency 等。它约束 root cause report 的分类。

具体例子：`RTL_STRUCTURAL_ISSUE` 必须有 RTL module path 和 interface 或 trace 证据。

### `shared/tables/rtl_module_catalog.yaml`

内容说明：该表定义可绑定的 RTL module 列表、memory path 分解和 `MODULE_BINDING_TEMPLATE`。它是 module binding rules 的机器可读目录。

具体例子：`lsq_template` 必须列出 required contract paths、required local state、input/output interfaces、partial sim cases、trace fields、forbidden hidden state 和 timing checks。

### `shared/tables/rtl_partial_sim_gate_table.yaml`

内容说明：该表定义每类 RTL module 的 partial simulation gate 和具体测试用例，包括 scoreboard、warp scheduler、load/store queue、shared memory bank unit 和 CSR runtime interface。它让局部仿真不只是形式化 PASS。

具体例子：LSQ gate 必须测试 ready low payload stable、tag unique、response wakeup 和 fault propagation；CSR runtime gate 必须测试 start、done、fault、kernel entry 和 arg base。

### `shared/tables/source_of_truth_generation_table.yaml`

内容说明：该表定义从 `SYSTEM_CONTRACT_IR` 生成或检查派生 artifact 的规则，并声明 docs、RTL defines、tool opcode table 都不能成为 truth source。它防止 artifact drift。

具体例子：ISA opcode table 必须从 `SYSTEM_CONTRACT_IR.isa_model.opcodes` 派生，不能由 `tools/isa.py` 单独定义。

### `shared/tables/trace_normalization_table.yaml`

内容说明：该表定义不同 trace 来源的字段映射和归一化规则，例如 runtime event、memory event、RTL waveform、golden trace、assembler/disassembler trace、program image trace 和 loader trace 到统一 schema 的映射。它支撑 correctness gate、first divergence、pass evidence 和 toolchain attribution。

具体例子：RTL `valid && ready` transaction 可以归一化成 `memory_request` event；assembler 编码证据可以归一化成带 `toolchain_artifact_path` 的 `assembler_encode` event。

### `shared/tests/architecture_generator/cases.yaml`

内容说明：该测试 case 文件验证 Architecture Generator 的输出，例如 intent lock、ARCH_IR、micro-constraint estimate 和 evidence 要求。它是文档型 regression。

具体例子：case 可以要求 vague design 缺少 validation target 时输出 `INSUFFICIENT_REQUEST`。

### `shared/tests/architecture_rewrite_loop_controller/cases.yaml`

内容说明：该测试 case 文件验证 Rewrite Loop Controller 的 rewrite trigger、patch taxonomy、owner 和 revalidation routing。它防止 controller 直接修改 IR 或乱归因。

具体例子：输入 `PERF_ATTRIBUTION_GRAPH` 中的 memory imbalance，应期望输出包含 patch target 和 required revalidation gates。

### `shared/tests/incremental_rtl_binding_engine/cases.yaml`

内容说明：该测试 case 文件验证 Incremental RTL Binding Engine 的 module binding、interface checker 和 partial sim evidence。它确保 RTL 绑定不是一次性全局生成。

具体例子：case 可以模拟 latency incompatible 的模块连接，并期望 `LATENCY_INCOMPATIBLE`。

### `shared/tests/simulation_performance_attribution_engine/cases.yaml`

内容说明：该测试 case 文件验证 trace ingestion、correctness gate、pass evidence、first divergence、performance metric、bottleneck graph、toolchain attribution 和 root cause engine 的行为。它要求通过和失败都必须有结构化证据。

具体例子：vector-add 通过时应期望 `PASS_EVIDENCE_REPORT` 和 `REGRESSION_FINGERPRINT`；assembler encoding mismatch 时应期望 `TOOLCHAIN_ATTRIBUTION_REPORT` 和 toolchain root cause。

### `shared/tests/system_contract_golden_engine/cases.yaml`

内容说明：该测试 case 文件验证 System Contract Golden Engine 的 contract freeze、golden semantics coverage 和 duplicate truth rejection。它保护唯一 truth source 规则。

具体例子：case 可以构造 golden model 自行定义 ISA opcode 的情况，并期望 `FORBIDDEN_GOLDEN_TRUTH`。

### `shared/tests/validate_v4_assets.py`

内容说明：这是当前 v5 资产校验脚本，虽然文件名保留 v4 字样，但内容已经验证 v5 self-correcting design-system contract。它检查旧 skill 不回流、shared 只保留 v5 资产、每个文件都有中文说明条目。

具体例子：如果新增 `shared/tables/new_table.yaml` 但没有更新允许列表和 `file_descriptions.zh.md`，脚本会报告 unexpected file 或 missing file description entry。

### `gpgpu-toolchain-runtime-artifact-engine/SKILL.md`

内容说明：这是 Toolchain Runtime Artifact Engine 的主 skill 文件，定义它如何从 `SYSTEM_CONTRACT_IR` 和 `GOLDEN_CONTRACT_MODEL` 派生 ISA table、assembler、disassembler、assembly IR、program image、runtime launch artifact、loader contract 和 smoke report。它强调这些工具产物不能重新定义 opcode、ABI、program image 或 loader truth。

具体例子：当 `SYSTEM_CONTRACT_IR.isa_model` 给出 opcode 和 instruction encoding 时，该 skill 负责生成 `TOOLCHAIN_ARTIFACT_IR` 并验证 assembler/disassembler/RTL defines 的 hash 一致，而不是手写第二套 opcode 表。

### `gpgpu-toolchain-runtime-artifact-engine/assembly_ir_rules.md`

内容说明：该文件定义 `ASSEMBLY_IR` 的字段、来源和 fail-closed 规则，明确第一阶段支持 hand-written assembly 或 lowered pseudo assembly，而不是完整 CUDA frontend。它让 assembly 到 program image 的闭环可先跑通。

具体例子：`input_kernel.asm` 中的 `lw r4, 0(r1)` 会被解析成带 `pc`、`mnemonic`、`operands`、`source_line` 和 `contract_path` 的 instruction record。

### `gpgpu-toolchain-runtime-artifact-engine/assembler_disassembler_roundtrip.md`

内容说明：该文件定义 assembler encode、disassembler decode 和 ASM -> bytes -> DISASM -> bytes roundtrip 三个 gate。它要求 unsupported instruction 行为、operand width、branch offset 和 field layout 都来自 `SYSTEM_CONTRACT_IR`。

具体例子：如果 `branch_equal` 的 offset 没按合同要求对齐，encode gate 应输出 `ASM_ENCODE_FAIL`；如果 disasm 后重新编码的 bytes 不一致，应输出 `DISASM_ROUNDTRIP_FAIL`。

### `gpgpu-toolchain-runtime-artifact-engine/isa_table_derivation.md`

内容说明：该文件说明如何从 `SYSTEM_CONTRACT_IR.isa_model` 派生 `tools/isa.py`、`tools/encoding_table.py`、assembler/disassembler table、RTL defines 和 ISA 文档。它定义 hash 等价检查，防止工具、RTL 和文档各自维护 opcode 真值。

具体例子：`isa_model_hash`、`assembler_table_hash`、`disassembler_table_hash` 和 `rtl_defines_hash` 不一致时，必须输出 `ISA_ENCODING_DRIFT` 或 `SOURCE_OF_TRUTH_DRIFT`。

### `gpgpu-toolchain-runtime-artifact-engine/program_image_and_loader_contract.md`

内容说明：该文件定义 `PROGRAM_IMAGE_IR` 和 `LOADER_CONTRACT_IR`，说明 text/data segment、symbol table、relocation、entry PC、imem/dmem 初始化和 RTL loader interface 如何绑定。它解决 RTL 从哪里取第一条指令、program image 如何进入 memory 的问题。

具体例子：vector-add 例子的 `vecadd` symbol 被解析为 `entry_pc: 0`，loader contract 要把 text segment 加载到 instruction memory，并在 reset 后让 entry PC 可见。

### `gpgpu-toolchain-runtime-artifact-engine/runtime_launch_artifact_rules.md`

内容说明：该文件定义 `RUNTIME_LAUNCH_IR`，包括 launch ABI、grid/block dim、warp size、arg buffer layout、CSR write sequence 和 completion observation。它把 runtime launch 从模糊概念变成可验证 artifact。

具体例子：vector-add launch artifact 会写入 `kernel_entry`、`arg_base`、`grid_dim`、`block_dim` 和 `start` CSR，并把 A/B/C 指针编码进 arg buffer。

### `gpgpu-toolchain-runtime-artifact-engine/toolchain_smoke_gates.md`

内容说明：该文件列出 toolchain smoke 的十个 gate，从 ISA table derivation 到 golden program image execution。它要求 golden model 执行从 `PROGRAM_IMAGE_IR` fetch/decode 出来的 instruction stream，而不是只跑抽象 instruction list。

具体例子：如果 program image 的 bytes 错了，golden image execution smoke 应在 memory dump 或 decoded trace 上暴露 `GOLDEN_IMAGE_EXECUTION_FAIL`。

### `shared/examples/self_correcting_minimal_simt/expected_assembly_ir.yaml`

内容说明：该示例文件给出 vector-add hand-written assembly 被解析后的 `ASSEMBLY_IR`，包括 sections、symbols、instructions、data objects、relocations 和 canonical hash。它是 toolchain stage 的最小输入 IR 示例。

具体例子：`lw r4, 0(r1)` 被记录为 `mnemonic: load_word`、`operands: [r4, 0, r1]`，并绑定到 `isa_model.opcodes.load_word`。

### `shared/examples/self_correcting_minimal_simt/expected_disassembly.asm`

内容说明：该文件给出 program bytes roundtrip 后期望得到的 canonical disassembly。它用于检查 disassembler decode 和 roundtrip gate。

具体例子：`expected_program.hex` 中的第三条指令应反汇编为 `add r6, r4, r5`，然后重新编码为同一条 bytes。

### `shared/examples/self_correcting_minimal_simt/expected_loader_contract_ir.yaml`

内容说明：该文件定义 vector-add program image 的 loader contract 示例，包括 imem/dmem load rule、entry PC rule、reset rule、RTL loader interface 和 memory initialization hash。

具体例子：loader 要把 text segment 放进 instruction memory，把 data segment 放进 global data memory，并声明 `arg_buffer_visible: before_start`。

### `shared/examples/self_correcting_minimal_simt/expected_memory_dump.yaml`

内容说明：该文件给出 golden program-image execution 后的期望内存 dump。它证明 golden model 是从 `PROGRAM_IMAGE_IR` fetch/decode/execute，而不是执行另一个抽象列表。

具体例子：输入 A=[1,2,3,4]、B=[10,20,30,40] 后，C 的 `words_u32` 必须是 `[11, 22, 33, 44]`。

### `shared/examples/self_correcting_minimal_simt/expected_program.hex`

内容说明：该文件给出 vector-add text segment 的最小 encoded instruction bytes，每行一条 32-bit 指令。它用于 assembler smoke、program image smoke 和 disassembler roundtrip。

具体例子：第一行 `0000a203` 对应示例中的第一条 `lw r4, 0(r1)`。

### `shared/examples/self_correcting_minimal_simt/expected_program_image_ir.yaml`

内容说明：该文件定义 vector-add 的 `PROGRAM_IMAGE_IR`，包含 text/data segments、symbol table、relocation table、initial memory objects 和 metadata hash。它是 loader、RTL image-load smoke 和 golden image execution 的共同输入。

具体例子：`entry_symbol: vecadd` 解析为 `entry_pc: 0`，data segment 中包含 A、B、C 三个 memory object。

### `shared/examples/self_correcting_minimal_simt/expected_runtime_launch_ir.yaml`

内容说明：该文件定义 vector-add 的 `RUNTIME_LAUNCH_IR`，包括 flat argument buffer、grid/block dim、warp size、CSR write sequence 和 completion observation。它让 runtime launch artifact 可被 RTL binding 消费。

具体例子：arg buffer 前 12 字节编码 A、B、C 三个 global pointer，CSR write sequence 以 `start=1` 结束。

### `shared/examples/self_correcting_minimal_simt/expected_toolchain_artifact_ir.yaml`

内容说明：该文件给出 toolchain stage 派生物总表，列出 ISA、assembler、disassembler、program image、runtime launch、loader artifacts 以及 source-of-truth hash 检查。它证明新增 stage 不拥有独立 truth。

具体例子：`assembler_table_hash`、`disassembler_table_hash` 和 `rtl_defines_hash` 都等于 `hash_isa_model_minimal_simt`。

### `shared/examples/self_correcting_minimal_simt/expected_toolchain_smoke_report.yaml`

内容说明：该文件记录 vector-add toolchain smoke 的期望结果，包括 ISA table、assembler parse/encode、disassembler decode/roundtrip、program image、runtime launch、loader 和 golden image execution gates。

具体例子：`golden_image_execution_result.verdict: PASS` 表示 program image 被 golden model 解码执行，并产生期望 memory dump。

### `shared/examples/self_correcting_minimal_simt/input_kernel.asm`

内容说明：该文件是最小 vector-add hand-written assembly 输入，用来驱动 `ASSEMBLY_IR`、assembler、program image 和 runtime launch 示例。它故意不是完整 CUDA frontend 输出。

具体例子：kernel 读取 A、B，执行 `add r6, r4, r5`，再把结果写入 C，对应 `C[i] = A[i] + B[i]` 的最小垂直切片。

### `shared/schemas/assembler_binding_report_ir.schema.yaml`

内容说明：该 schema 定义 assembler/disassembler binding report 的字段，包括 encode、decode、roundtrip、unsupported instruction 和 source-of-truth checks。它让 toolchain smoke 的错误可被 attribution/rewrite 消费。

具体例子：当 `DISASM_ROUNDTRIP_FAIL` 出现时，report 应记录失败 instruction、encoded bytes、decoded form 和相关 source-of-truth hash。

### `shared/schemas/assembly_ir.schema.yaml`

内容说明：该 schema 定义 `ASSEMBLY_IR` 的最小字段，包括 contract hash、source kind、sections、symbols、instructions、relocations 和 canonical hash。它是 assembler 输入的结构化合同。

具体例子：hand-written assembly 和 lowered pseudo assembly 都必须先转成该 schema，才能进入 assembler encode gate。

### `shared/schemas/loader_contract_ir.schema.yaml`

内容说明：该 schema 定义 `LOADER_CONTRACT_IR`，包括 program image hash、imem/dmem load rule、entry PC rule、reset rule、RTL loader interface 和 memory initialization hash。它约束 RTL image-load 入口。

具体例子：RTL binding 如果不知道 entry PC 来自哪里，就无法满足该 schema 的 `entry_pc_rule`。

### `shared/schemas/program_image_ir.schema.yaml`

内容说明：该 schema 定义 `PROGRAM_IMAGE_IR`，包括 image format version、entry symbol、entry PC、segments、symbol/relocation table、metadata 和 canonical hash。它是 assembler 到 RTL/golden 的二进制桥梁。

具体例子：program image 的 text segment bytes 同时被 disassembler roundtrip、golden execution 和 RTL instruction memory init 使用。

### `shared/schemas/runtime_launch_ir.schema.yaml`

内容说明：该 schema 定义 `RUNTIME_LAUNCH_IR`，包括 launch ABI、entry PC、grid/block dim、arg buffer、CSR write sequence、completion observation 和 canonical hash。它约束 runtime artifact 如何驱动 RTL。

具体例子：`csr_write_sequence` 缺少 `start` 写入时，runtime launch smoke 应输出 `RUNTIME_ARG_ENCODING_FAIL` 或相关 launch artifact failure。

### `shared/schemas/toolchain_artifact_ir.schema.yaml`

内容说明：该 schema 定义 `TOOLCHAIN_ARTIFACT_IR`，汇总 ISA、assembler、disassembler、program image、runtime launch、loader artifacts、artifact hashes 和 source-of-truth checks。它是新增第 3 阶段的主输出。

具体例子：如果 `tools/assembler.py` 的 opcode table hash 与 `SYSTEM_CONTRACT_IR.isa_model` 不一致，该 IR 的 `source_of_truth_checks` 必须失败。

### `shared/schemas/toolchain_smoke_report_ir.schema.yaml`

内容说明：该 schema 定义 toolchain smoke report，包括各 gate 结果、golden image execution result、evidence hashes 和 verdict。它让 toolchain stage 的 smoke 结果可被后续 trace attribution 使用。

具体例子：program image layout smoke 失败时，report 可把 failure mode 传给 root cause taxonomy 的 `PROGRAM_IMAGE_LAYOUT_MISMATCH`。

### `shared/tables/assembly_syntax_table.yaml`

内容说明：该表定义 assembly syntax 的合同来源，包括 register naming、immediate formats、label syntax、section syntax 和 comment syntax。它防止 assembler parser 自己发明语法。

具体例子：寄存器名 `r0` 到 `r31` 的合法性来自 `SYSTEM_CONTRACT_IR.isa_model.assembly_syntax.register_naming`。

### `shared/tables/instruction_encoding_derivation_table.yaml`

内容说明：该表定义 instruction encoding 的派生来源和等价 hash，包括 opcode、encoding layout、operand fields、decode classes、assembler/disassembler/RTL hash。它是防 drift 的机器可读规则。

具体例子：`rtl_defines_hash` 和 `assembler_table_hash` 不一致时，该表要求 `ISA_ENCODING_DRIFT`。

### `shared/tables/loader_contract_table.yaml`

内容说明：该表定义 loader contract 的来源和 RTL loader interfaces，包括 program image loader、instruction memory init 和 runtime arg buffer interface。它让 loader 行为有明确 owner。

具体例子：`instruction_memory_init` 必须从 `launch_model.loader_contract.imem_load_rule` 派生，而不能由 RTL testbench 自行规定。

### `shared/tables/program_image_format_table.yaml`

内容说明：该表定义 program image format 的 segment、metadata hash、entry symbol resolution 和 failure mode。它把 image layout 从隐含约定变成显式合同。

具体例子：text segment 权限必须是 `rx`，entry symbol 解析失败应输出 `ENTRY_SYMBOL_RESOLVE_FAIL`。

### `shared/tables/runtime_launch_binding_table.yaml`

内容说明：该表定义 runtime launch artifact 如何绑定到 launch model，包括 ABI、grid/block mapping、kernel entry、argument buffer、CSR write sequence 和 completion observation。它约束 runtime launch 产物。

具体例子：CSR write sequence 必须包含 `kernel_entry`、`arg_base`、`grid_dim`、`block_dim` 和 `start`。

### `shared/tables/toolchain_artifact_generation_table.yaml`

内容说明：该表定义从 `SYSTEM_CONTRACT_IR` 到 toolchain 文件的派生关系，包括 ISA、launch、program image 和 loader artifacts。它是新增 toolchain stage 的 generation rule 总表。

具体例子：`SYSTEM_CONTRACT_IR.isa_model` 派生 `tools/isa.py`、`tools/encoding_table.py`、`tools/assembler.py`、`tools/disassembler.py`、`rtl/defines.svh` 和 `docs/isa.md`。

### `shared/tables/toolchain_validation_gate_table.yaml`

内容说明：该表定义 toolchain smoke gates，包括 ISA table derivation、assembler parse/encode、disassembler decode/roundtrip、program image、entry symbol、runtime launch、loader 和 golden image execution。它是 toolchain stage 的验证门。

具体例子：`golden_image_execution_smoke` 输入 `PROGRAM_IMAGE_IR`，输出 expected memory dump，失败为 `GOLDEN_IMAGE_EXECUTION_FAIL`。

### `shared/tests/toolchain_runtime_artifact_engine/cases.yaml`

内容说明：该测试 case 文件验证 Toolchain Runtime Artifact Engine 能从 system contract、golden model 和 input assembly 派生完整工具链 artifacts。它是新增第 3 阶段的 regression case。

具体例子：case 要求输出 `TOOLCHAIN_ARTIFACT_IR`、`ASSEMBLY_IR`、`PROGRAM_IMAGE_IR`、`RUNTIME_LAUNCH_IR`、`LOADER_CONTRACT_IR` 和 `TOOLCHAIN_SMOKE_REPORT`。

### `shared/schemas/correctness_gate_report_ir.schema.yaml`

内容说明：该 schema 定义 `CORRECTNESS_GATE_REPORT`，包括 correctness verdict、selected mode、comparison level、mismatch summary、evidence completeness 和 fail reason。它是 simulation attribution 从 trace normalization 进入 failure mode 或 pass mode 的分流结构。

具体例子：final memory mismatch 时该 report 选择 `FAILURE_ATTRIBUTION_MODE`；final memory 一致但缺少 golden trace 时选择 `PASS_EVIDENCE_MODE` 并输出 `PASS_WITH_INSUFFICIENT_EVIDENCE`。

### `shared/schemas/first_divergence_report_ir.schema.yaml`

内容说明：该 schema 定义 `FIRST_DIVERGENCE_REPORT`，记录 first divergence type、cycle/step、warp、PC、golden/RTL event、contract path、RTL module path、toolchain artifact path、pre/post window、evidence hash 和 confidence。

具体例子：active mask 第一次不一致时，report 可以填 `ACTIVE_MASK_MISMATCH`、对应 warp id、PC、golden event、RTL event 和 SIMT stack module path。

### `shared/schemas/pass_evidence_report_ir.schema.yaml`

内容说明：该 schema 定义 `PASS_EVIDENCE_REPORT`，包括 pass verdict、evidence completeness、architectural state comparison、coverage/metric/fingerprint 引用和 warnings。它让通过用例也能留下可回归证据。

具体例子：vector-add final memory 与 golden 一致时，report 会记录 final memory match、completion/fault match、RTL trace 是否存在，以及 coverage 和 regression fingerprint 的引用。

### `shared/schemas/performance_metric_ir.schema.yaml`

内容说明：该 schema 定义 `PERFORMANCE_METRIC_IR`，记录 cycles、IPC、warp eligible/issue rate、issue utilization、pipeline utilization、stall breakdown、memory metrics、scheduler metrics、warning flags 和 metric hash。

具体例子：一个 pass case 的 `stall_breakdown.memory_wait` 很高时，metric report 会携带 `HIGH_MEMORY_STALL`，供 bottleneck graph 判断是否需要 architecture rewrite。

### `shared/schemas/regression_fingerprint_ir.schema.yaml`

内容说明：该 schema 定义 `REGRESSION_FINGERPRINT`，把 contract、golden、RTL、toolchain、program image、runtime launch、loader、input/final memory、trace summary、performance metric 和 coverage hash 组合成稳定回归指纹。

具体例子：同一 vector-add case 在 RTL 改动后 final memory 仍一致，但 `performance_metric_hash` 改变，可以用该 fingerprint 发现性能回归。

### `shared/schemas/stall_breakdown_ir.schema.yaml`

内容说明：该 schema 定义 stall breakdown 的标准字段，包括 scoreboard dependency、no ready warp、memory wait、LSQ full、coalescer wait、bank conflict、barrier wait、divergence reconvergence、register file port conflict、pipeline busy、interface backpressure、runtime wait 和 unknown。

具体例子：scheduler underutilization case 会同时观察 `no_ready_warp` 和 `scoreboard_dependency`，避免只用一个粗略 stall 计数判断瓶颈。

### `shared/schemas/toolchain_attribution_report_ir.schema.yaml`

内容说明：该 schema 定义 `TOOLCHAIN_ATTRIBUTION_REPORT`，记录 toolchain verdict、checked chain、failure point、related contract paths、related artifacts 和 evidence hashes。它让 simulation attribution 能把错误路由到 assembler/program image/loader/runtime 或 RTL。

具体例子：program image entry PC 错时，report 的 failure point 是 `ENTRY_SYMBOL_RESOLUTION`，related contract path 指向 `launch_model.program_image_format` 和 loader contract。

### `shared/schemas/trace_coverage_report_ir.schema.yaml`

内容说明：该 schema 定义 `TRACE_COVERAGE_REPORT`，记录 observed/uncovered contract paths、observed RTL module paths、observed toolchain artifact paths、source completeness、coverage hash 和 warnings。

具体例子：通过用例没有覆盖 barrier contract path 时，该 report 会把该 path 放入 `uncovered_contract_paths`，pass evidence 可以降级为 evidence warning。

### `shared/schemas/trace_source_manifest_ir.schema.yaml`

内容说明：该 schema 定义 trace source manifest，记录输入 trace source 列表、source hashes、missing sources、evidence completeness、toolchain artifact paths、RTL module paths 和 contract paths。它是 trace ingestion 的证据目录。

具体例子：一个 failure case 同时提供 assembler trace、program image trace、RTL trace 和 golden trace，该 manifest 会记录每个 source 的 hash，供 regression fingerprint 和 toolchain attribution 使用。

### `shared/tables/bottleneck_template_table.yaml`

内容说明：该表定义 bottleneck graph 的模板集合，包括 memory latency、shared bank conflict、scoreboard dependency、scheduler underutilization、barrier synchronization、branch divergence、pipeline imbalance、interface backpressure、toolchain mismatch 和 runtime launch mismatch。

具体例子：`shared_bank_conflict_template` 要求 cycle window、warp、bank conflict、RTL pipeline stage 和 contract rule 节点齐全，才能输出 bank conflict 瓶颈。

### `shared/tables/correctness_gate_decision_table.yaml`

内容说明：该表定义 correctness gate 的判定顺序和比较层级，用 final memory、completion/fault、architectural state、trace divergence、evidence completeness 决定 verdict 和 selected mode。

具体例子：completion status mismatch 排在 evidence incomplete 之前，因此即使 trace 不完整，也要先进入 failure attribution mode 处理 completion/fault 问题。

### `shared/tables/differential_compare_table.yaml`

内容说明：该表定义 differential correctness 的比较顺序和各 divergence type 所需字段，确保 first divergence 从 PC、decode、mask、writeback、memory、CSR、barrier、fault、completion 等证据中按确定顺序选择。

具体例子：`MEMORY_BYTE_ENABLE_MISMATCH` 需要 `byte_enable` 和 `lane_mask`，如果这些字段缺失，不能猜测 byte enable 根因，只能输出 insufficient trace。

### `shared/tables/event_type_taxonomy.yaml`

内容说明：该表定义 normalized event type taxonomy，把 fetch、decode、issue、execute、writeback、commit、branch、divergence、barrier、memory、CSR、runtime、toolchain 和 fault 事件归类。

具体例子：`assembler_encode` 属于 toolchain class，而 `decode` 属于 architectural class；toolchain attribution 和 first divergence 比较会按类别选择不同规则。

### `shared/tables/minimal_trace_window_table.yaml`

内容说明：该表定义 correctness window 和 performance window 的默认窗口规则，包括 pre/post event 数、dependency closure、contract/RTL/toolchain path 包含规则，以及 performance window 的 tie breakers。

具体例子：多个 stall window 贡献接近时，先选证据完整度最高的窗口，再选最早窗口和 contract/RTL 映射最强的窗口。

### `shared/tables/pass_evidence_gate_table.yaml`

内容说明：该表定义 pass evidence 的必需检查项和 warning 到 verdict 的映射，包括 hash completeness、architectural comparison、regression fingerprint 字段、missing trace、uncovered contract path、performance warning 和 trace divergence。

具体例子：final memory pass 但 `completion_status_present` 为 false 时，pass report 要输出 `PASS_WITH_INSUFFICIENT_EVIDENCE`，不能输出 clean correctness pass。

### `shared/tables/performance_metric_table.yaml`

内容说明：该表定义性能指标提取等级和 warning threshold 名称，从 correctness-only smoke 到 standard validation 再到 performance gate，规定哪些指标必需以及是否必须构建 graph。

具体例子：performance gate 要求 IPC、issue utilization、pipeline utilization、stall breakdown、memory metrics 和 scheduler metrics，并要求构建 `PERF_ATTRIBUTION_GRAPH`。

### `shared/tables/report_generation_table.yaml`

内容说明：该表定义 `SIM_PERF_ATTRIBUTION_REPORT` 在 failure mode 和 pass mode 下的 required refs、optional refs、correctness/performance/evidence verdict 枚举，以及 human summary 字段。

具体例子：pass mode 必须引用 correctness gate、pass evidence、trace coverage、performance metric 和 regression fingerprint；failure mode 必须引用 first divergence 和 root cause。

### `shared/tables/stall_reason_taxonomy.yaml`

内容说明：该表把标准 stall reason 映射到 root cause family，包括 scoreboard、no ready warp、memory wait、LSQ full、coalescer wait、bank conflict、barrier、divergence、register file port conflict、pipeline busy、interface backpressure、runtime wait 和 unknown。

具体例子：`interface_backpressure` 默认归入 `RTL_INTERFACE_ROOT_CAUSE`，而不是 memory bottleneck，除非 graph 证据进一步指向 memory system。

### `shared/tables/toolchain_attribution_taxonomy.yaml`

内容说明：该表把 toolchain failure point 映射到 root cause class/subclass，并列出 checked chain fields。它让 assembler、disassembler、program image、entry symbol、loader、runtime arg、RTL fetch/decode 的错误有稳定归因。

具体例子：`ASM_ENCODE` 映射到 `TOOLCHAIN_ROOT_CAUSE/ASM_ENCODE_MISMATCH`，`RUNTIME_ARG_ENCODING` 映射到 `RUNTIME_LAUNCH_ROOT_CAUSE/ARG_BUFFER_ENCODING_MISMATCH`。

### `shared/tables/trace_source_manifest_table.yaml`

内容说明：该表定义各 trace source 在不同模式或 root cause 下的要求和 hash 字段，包括 RTL、waveform、golden、module partial sim、memory、runtime launch、assembler、disassembler、program image、loader 和 toolchain smoke trace。

具体例子：toolchain root cause 需要 assembler/disassembler/program image/loader/toolchain smoke trace 的 hash；pass evidence mode 至少需要 memory、runtime launch、RTL 或可说明的 missing source。

### `skill_5stage_compression_plan.zh.md`

内容说明：这是中文实施计划文档，记录从 9-stage/4-layer 结构升级为 self-correcting GPGPU design system 的理由、模块职责、缺口补齐、资产创建和迁移策略。文件开头补充了当前 6-stage 更新说明，指出新增 toolchain runtime artifact stage 后以 `README.md` 和 flow 文档为准。

具体例子：维护者想知道为什么 closure 不再只是 report，而是 rewrite loop controller，或为什么 toolchain artifact 要独立成 stage，可以在该计划和更新说明中找到背景。

### `skill_summary.md`

内容说明：这是重写后的中文总览，面向快速阅读者概括当前 v5 skill 系统、六个核心 skill、shared 资产边界、旧 skill 删除状态和验证方式。它比详细计划更短，适合作为日常入口。

具体例子：新 agent 接手任务时，可以先读 `skill_summary.md` 确认当前架构，再按需进入 `file_descriptions.zh.md` 查单个文件用途。
