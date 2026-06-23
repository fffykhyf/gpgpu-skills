# Skill 文件中文说明索引

## 覆盖规则

本文件覆盖 `skill/` 仓库中除 `.git/` 以外的每一个子文件。每个条目都说明该文件放了什么内容、它在 GPGPU skill 体系中的作用，并给出一个具体例子，方便后续维护者快速判断文件是否还能删除、迁移或扩展。

### `README.md`

内容说明：这是 `skill/` 仓库的入口说明，概括 self-correcting GPGPU design system 的目标、五个顶层 skill、核心输出、legacy 迁移原则和 shared 资产边界。它告诉读者当前仓库已经不是旧 9-stage pipeline，而是以可执行合同、增量 RTL、因果归因和 rewrite loop 为核心的 v5 skill 系统。

具体例子：新维护者打开仓库时，可以先读这里确认当前只应调用 `gpgpu-architecture-generator`、`gpgpu-system-contract-golden-engine`、`gpgpu-incremental-rtl-binding-engine`、`gpgpu-simulation-performance-attribution-engine`、`gpgpu-architecture-rewrite-loop-controller` 五个 GPGPU skill。

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

内容说明：这是 Architecture Rewrite Loop Controller 的主 skill 文件，定义它如何消费 `PERF_ATTRIBUTION_GRAPH`、`ROOT_CAUSE_REPORT`、`ARCH_IR`、`SYSTEM_CONTRACT_IR` 和 `INCREMENTAL_RTL_MAP`，并生成 `ARCH_REWRITE_PLAN`、`REWRITE_DECISION_REPORT` 与 `REGRESSION_TRACKING_REPORT`。它强调 controller 只能提出 patch plan，不能直接修改 IR。

具体例子：如果 perf graph 显示 shared memory bank conflict 导致大量 warp stall，该 skill 可以输出一个 RTL Patch 或 Architecture Patch 计划，并列出必须重跑的 revalidation gates。

### `gpgpu-architecture-rewrite-loop-controller/legacy_closure_repair_constraints.md`

内容说明：该文件迁移旧 closure refinement 和 synthesis closure 的 gate、repair routing、failure attribution 规则。它把旧的 `ACCEPT`、`REJECT`、`REFINE_REQUIRED`、`INSUFFICIENT_EVIDENCE` 映射到 v5 rewrite decision 语义。

具体例子：旧系统中的 `MEMORY_DUMP_CONTRACT_MISMATCH` 现在会成为 rewrite controller 的故障标签，并被映射到 RTL Patch 或 Test Evidence Patch，而不是重新启用旧 closure skill。

### `gpgpu-architecture-rewrite-loop-controller/patch_taxonomy.md`

内容说明：该文件定义 rewrite plan 可使用的 patch 类型，包括 Architecture Patch、Contract Patch、RTL Patch 和 Test Evidence Patch。它让 controller 对“该改架构、合同、RTL 还是测试证据”有稳定分类。

具体例子：如果 root cause 是 `SCHEDULER_INEFFICIENCY`，可以归类为 Architecture Patch；如果是 `PIPELINE_BOUNDARY_FAIL`，更可能归类为 RTL Patch。

### `gpgpu-architecture-rewrite-loop-controller/regression_tracking.md`

内容说明：该文件说明 rewrite loop 必须如何记录 regression risk、历史失败、已应用 patch 和后续验证结果。它避免系统只修当前失败，却忘记历史通过的行为。

具体例子：一次把 warp size 从 8 改到 16 的 Architecture Patch，必须记录可能影响 active mask、register pressure 和 occupancy 的 regression risk。

### `gpgpu-architecture-rewrite-loop-controller/revalidation_routing.md`

内容说明：该文件定义不同 patch 类型需要重新路由到哪些模块和 gate。它把 rewrite plan 和后续验证连接起来，避免 patch 只停留在建议文本。

具体例子：RTL Patch 应重新进入 Incremental RTL Binding Engine 并跑 interface check、partial sim，再进入 Simulation Performance Attribution Engine 做 trace 对比。

### `gpgpu-architecture-rewrite-loop-controller/rewrite_trigger.md`

内容说明：该文件描述 root cause 如何触发 rewrite。它规定只有证据足够、owner 明确、revalidation route 存在时，controller 才能产生 rewrite plan。

具体例子：`PERF_CAUSAL_CHAIN_MISSING` 不能直接触发架构改动，而应先触发 Test Evidence Patch，要求补齐 trace evidence。

### `gpgpu-incremental-rtl-binding-engine/SKILL.md`

内容说明：这是 Incremental RTL Binding Engine 的主 skill 文件，定义它如何把 `SYSTEM_CONTRACT_IR` 和 `GOLDEN_CONTRACT_MODEL` 逐模块绑定成 `INCREMENTAL_RTL_MAP`。它强调 module-by-module assembly、interface contract checking 和 RTL partial simulation。

具体例子：在实现 load/store queue 时，该 skill 要求声明 consumed contract paths、provided signals、latency contract、local trace schema，并用 golden slice 做局部仿真对比。

### `gpgpu-incremental-rtl-binding-engine/interface_contract_checker.md`

内容说明：该文件说明接口合同检查器要检查信号一致性、握手协议、latency compatibility、pipeline boundary 和 reset/stall/backpressure 传播。它是防止模块拼接后才暴露接口错误的约束文档。

具体例子：如果 LSQ 输出 `mem_req_valid` 但 cache interface 要求 `req_valid` 且 tag width 不同，checker 必须报告 `INTERFACE_PROTOCOL_MISMATCH` 或 width mismatch。

### `gpgpu-incremental-rtl-binding-engine/legacy_binding_and_module_constraints.md`

内容说明：该文件迁移旧 artifact-contract、memory-subsystem、runtime hardware interface、deterministic transform 和 RTL SIMT core 中有价值的绑定规则。它把这些旧规则归并到 v5 的增量 RTL 绑定层。

具体例子：旧系统中“每个 generated artifact 必须携带 state hash”的思想，在这里迁移为每个 RTL module binding 必须携带 source contract hash 和 golden model hash。

### `gpgpu-incremental-rtl-binding-engine/module_builder.md`

内容说明：该文件定义 module-by-module RTL builder 的行为，说明每个模块需要声明 module contract、local state binding、input/output interface、local trace 和 partial simulation evidence。

具体例子：构建 warp scheduler module 时，需要声明它消费 scheduler policy contract path，输出 selected warp id，并记录 scoreboard stall 的 local trace。

### `gpgpu-incremental-rtl-binding-engine/module_catalog.md`

内容说明：该文件列出 v5 RTL binding 需要考虑的模块目录，例如 SM core、warp scheduler、execute pipeline、register file、scoreboard、LSQ、shared memory、cache/global interface、CSR runtime interface 等。

具体例子：一个 minimal SIMT 设计可以只实例化 SM core、warp scheduler、integer pipeline、register file、scoreboard 和 global memory interface，并显式标记 shared memory 为 non-goal。

### `gpgpu-incremental-rtl-binding-engine/rtl_partial_simulator.md`

内容说明：该文件说明每个 RTL module 在进入 full-system simulation 前要先做局部仿真，并与对应的 `GOLDEN_CONTRACT_MODEL` slice 对齐。它要求输出 local trace、scoreboard check 和 mismatch report。

具体例子：对 scoreboard module，partial sim 应输入 register dependency 序列，检查 ready bit 和 wakeup event 是否与 golden dependency rule 一致。

### `gpgpu-simulation-performance-attribution-engine/SKILL.md`

内容说明：这是 Simulation Performance Attribution Engine 的主 skill 文件，定义如何归一化 runtime、memory、RTL、waveform、module partial sim 和 golden trace，并生成 `NORMALIZED_TRACE_IR`、`PERF_ATTRIBUTION_GRAPH` 与 `ROOT_CAUSE_REPORT`。它要求性能结论必须有跨层因果链。

具体例子：当 kernel 变慢时，该 skill 不能只说“memory bottleneck”，必须连接 cycle、warp、memory request、cache miss、RTL module path 和 contract path。

### `gpgpu-simulation-performance-attribution-engine/bottleneck_graph_builder.md`

内容说明：该文件说明如何把 trace event 构造成 bottleneck graph，将 stall、scoreboard dependency、memory request、cache miss、pipeline stage 和 contract rule 串成因果链。

具体例子：一个 warp stall node 可以连接到 scoreboard dependency node，再连接到 LSQ memory request node，最终指向 cache_global_interface 的 miss response 延迟。

### `gpgpu-simulation-performance-attribution-engine/legacy_validation_and_trace_constraints.md`

内容说明：该文件迁移旧 runtime validator、memory validation、implementation validator、golden sim 和 causal trace analyzer 中仍有价值的验证规则。它把旧的 compile smoke、assembler smoke、memory dump compare 和 first divergence 都纳入 v5 trace attribution。

具体例子：旧 `APP_COMPILE_FAIL` 不再由 runtime-validator 独立处理，而是作为 Test Evidence 或 root cause 输入，被归一化进 `ROOT_CAUSE_REPORT`。

### `gpgpu-simulation-performance-attribution-engine/root_cause_engine.md`

内容说明：该文件定义 root cause engine 如何根据 normalized trace 和 bottleneck graph 判断故障类别。它要求 root cause 必须引用 contract path、RTL module path 或明确说明 evidence 不足。

具体例子：如果寄存器写回值和 golden trace 在第 42 cycle 第一次分歧，root cause engine 应输出涉及的 instruction、warp、RTL module 和 contract transition path。

### `gpgpu-simulation-performance-attribution-engine/trace_normalizer.md`

内容说明：该文件说明如何统一 RTL trace、golden trace、runtime launch trace、memory trace 和 partial simulation trace 的字段名、时间基准、事件类型和 path 映射。

具体例子：RTL 里的 `pc_q`、golden trace 里的 `warp.pc` 和 waveform dump 里的 `u_fetch.pc` 需要归一化到同一个 `pc` event field。

### `gpgpu-system-contract-golden-engine/SKILL.md`

内容说明：这是 System Contract + Golden Semantics Engine 的主 skill 文件，定义它如何把 `ARCH_IR` 冻结为唯一 truth source `SYSTEM_CONTRACT_IR`，并派生可执行 reference semantics `GOLDEN_CONTRACT_MODEL`。它是 v5 系统唯一的语义冻结层。

具体例子：当 `ARCH_IR` 选择 `ROUND_ROBIN` scheduler 时，该 skill 要把调度规则写进 `SYSTEM_CONTRACT_IR`，再生成可执行的 scheduler reference function。

### `gpgpu-system-contract-golden-engine/execution_semantics.md`

内容说明：该文件描述 execution contract 如何 lowering 成可执行语义，包括 warp scheduling、active mask update、divergence/reconvergence、scoreboard dependency 和 commit rule。

具体例子：对于分支发散，golden execution semantics 应根据 active mask 和 reconvergence rule 计算下一步执行 lane，而不是让 RTL validator 自己猜测。

### `gpgpu-system-contract-golden-engine/golden_model_contract.md`

内容说明：该文件定义 `GOLDEN_CONTRACT_MODEL` 的边界：它只能执行 `SYSTEM_CONTRACT_IR` 中冻结的语义，不能成为第二套 ISA、memory 或 scheduler truth。

具体例子：golden model 可以实现 `coalesce(load_requests)` reference function，但该函数必须引用 memory contract path，不能自行选择新的 coalescing policy。

### `gpgpu-system-contract-golden-engine/launch_semantics.md`

内容说明：该文件描述 launch contract 的可执行语义，包括 ABI decode、grid/block/thread mapping、kernel entry、CSR-visible launch state、completion 和 fault observation。

具体例子：host 写 doorbell 后，launch semantics 应确定 blockDim、gridDim、entry PC 和 thread id mapping，并把 completion event 写入可观察状态。

### `gpgpu-system-contract-golden-engine/legacy_spec_state_truth_constraints.md`

内容说明：该文件迁移旧 spec-lock、canonical-state-engine、artifact truth、runtime launch truth、memory truth、config 和 golden sim 中仍有价值的 truth 规则。它强调所有 truth definition 只能落在 `SYSTEM_CONTRACT_IR` 中。

具体例子：旧 canonical state 中的 `pc_table`、`exec_mask_table`、scoreboard state 会迁移为 system contract 的 state model，而不是保留一个单独的 state engine skill。

### `gpgpu-system-contract-golden-engine/memory_semantics.md`

内容说明：该文件描述 memory contract 如何变成可执行 reference semantics，包括 address-space resolver、coalescing、byte enable、ordering、fence、atomic 和 request lifecycle。

具体例子：对一次 warp load，memory semantics 应根据 lane mask 和 access size 计算 byte enable 与 coalesced request，而不是等 RTL trace 之后再定义行为。

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

内容说明：该 schema 定义候选 `ARCH_IR` 的结构，包括设计身份、compute topology、execution model、memory hierarchy、launch ABI、config contract 和 provenance。它是架构候选图的结构合同。

具体例子：`ARCH_IR.compute_topology.warp_size` 可以是 8，但该值仍是候选架构参数，不是最终 semantic truth。

### `shared/schemas/arch_rewrite_plan.schema.yaml`

内容说明：该 schema 定义 `ARCH_REWRITE_PLAN`，包括 rewrite id、patch type、owner module、patch target、expected impact、required revalidation gates 和 regression risk。它约束 rewrite loop 的输出。

具体例子：一个 RTL Patch 计划必须包含目标模块如 `load_store_queue`，以及需要重跑的 `partial_sim` 和 trace attribution gate。

### `shared/schemas/contract_semantics_report_ir.schema.yaml`

内容说明：该 schema 定义 contract semantics report，用来记录 `SYSTEM_CONTRACT_IR` 到 `GOLDEN_CONTRACT_MODEL` 的覆盖、失败路径和禁止独立 truth 检查。它验证合同语义可执行。

具体例子：如果 memory ordering path 没有对应 reference function，报告应记录 `CONTRACT_PATH_UNMAPPED`。

### `shared/schemas/design_intent_ir.schema.yaml`

内容说明：该 schema 定义 `DESIGN_INTENT_IR`，用于锁定用户目标、workload、target platform、validation target、non-goals 和 provenance。它只表达意图，不表达最终架构 truth。

具体例子：用户要求“教学用、可跑 vector add”，这里应记录 workload profile 和 validation target，而不是直接写死 cache policy。

### `shared/schemas/golden_contract_model.schema.yaml`

内容说明：该 schema 定义 `GOLDEN_CONTRACT_MODEL` 的结构，要求 executable semantics function 映射到 contract path，并携带 contract hash 和 coverage。它防止 golden model 变成第二套真值。

具体例子：`coalescing_reference` 函数必须声明它来自 `SYSTEM_CONTRACT_IR.memory_model.coalescing_rule`。

### `shared/schemas/incremental_rtl_map.schema.yaml`

内容说明：该 schema 定义 `INCREMENTAL_RTL_MAP`，描述 module-by-module RTL binding 的模块、接口、latency contract、local trace schema 和 partial sim evidence。它替代旧的全局 RTL map。

具体例子：`scoreboard` module 条目必须声明 consumed contract paths 和 provided wakeup signal。

### `shared/schemas/micro_constraint_estimate_ir.schema.yaml`

内容说明：该 schema 定义 `MICRO_CONSTRAINT_ESTIMATE_IR`，记录 area、memory pressure、occupancy、register pressure、bandwidth need 和 risk assumptions。它用于早期发现不可实现架构。

具体例子：一个 candidate 如果 bandwidth_need 大于 target platform 上限，应在 `known_unrealizable_risks` 中列出。

### `shared/schemas/mode_selection_ir.schema.yaml`

内容说明：该 schema 定义 `MODE_SELECTION_IR`，记录请求属于 design、reproduce、patch request 还是 trace debug，以及下一步应进入哪个当前 v5 owner。它是请求入口的路由结构。

具体例子：用户提供 trace 和 divergence report 时，mode selection 应指向 Simulation Performance Attribution Engine。

### `shared/schemas/module_interface_report_ir.schema.yaml`

内容说明：该 schema 定义 module interface report，用于记录信号、握手、latency、pipeline boundary 和 reset/backpressure 检查结果。它是 Incremental RTL Binding 的接口质量证据。

具体例子：如果 `req_ready` 没有在 stall 时传播，该 report 应标记 interface protocol failure。

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

内容说明：该 schema 定义 RTL partial simulation report，记录单模块局部仿真输入、输出、golden slice 对比和 mismatch。它让 RTL module 在整机仿真前先过局部门槛。

具体例子：对 LSQ 模块，partial sim report 应包含 request tag、load/store ordering 和 wakeup event 的对比结果。

### `shared/schemas/sim_perf_attribution_report_ir.schema.yaml`

内容说明：该 schema 定义 Simulation Performance Attribution Engine 的总报告结构，汇总 normalized trace、perf graph、root cause、minimal trace window 和 evidence hashes。

具体例子：一次 RTL/golden mismatch 调试完成后，该 report 应指向 first divergence window 和 root cause report hash。

### `shared/schemas/system_contract_ir.schema.yaml`

内容说明：该 schema 定义 `SYSTEM_CONTRACT_IR`，也就是唯一语义真值层，覆盖 execution model、state model、memory model、launch model 和 config contract。它是 Golden Semantics、RTL Binding 和 Verification 的共同基础。

具体例子：warp active mask、PC state、memory ordering 和 launch ABI 都应在此冻结，而不是分散在 validator 或 RTL 文件中。

### `shared/tables/architecture_preset_library.yaml`

内容说明：该表定义 Architecture Generator 可选的架构 preset，例如 minimal SIMT、multi-warp single SM 和 vertical slice GPGPU。它为候选架构提供可追踪起点。

具体例子：用户要求“教学用最小 GPU”时，generator 可以选择 `MINIMAL_SIMT_CORE` 作为候选 preset。

### `shared/tables/config_ownership_table.yaml`

内容说明：该表定义 config 字段的 owner、可见性和消费者，例如 `warp_size`、`trace_enable`、`block_dim` 等。它防止 runtime、RTL、simulator 随意修改配置真值。

具体例子：`warp_size` 由 System Contract Golden Engine 拥有，runtime 和 RTL 只能消费该字段。

### `shared/tables/contract_semantics_binding_table.yaml`

内容说明：该表把 `SYSTEM_CONTRACT_IR` 路径绑定到 executable semantics function，例如 scheduler、divergence、coalescing、ABI decode。它确保每个可执行函数都有合同来源。

具体例子：`memory_model.coalescing` 可以绑定到 `coalescing_reference_function`。

### `shared/tables/enum_table.yaml`

内容说明：该表定义系统允许使用的枚举值，如 scheduler policy、cache policy、launch ABI、provenance 等。它阻止 hidden default 和 unknown enum 进入 IR。

具体例子：如果用户要求未登记的 warp scheduling policy，generator 或 contract engine 应拒绝而不是猜测。

### `shared/tables/golden_model_coverage_table.yaml`

内容说明：该表定义 golden model 必须覆盖的 contract semantics 路径和 coverage gate。它用于判断 `GOLDEN_CONTRACT_MODEL` 是否完整执行合同。

具体例子：如果 launch ABI decode 没有 golden function，对应 coverage gate 应失败。

### `shared/tables/hard_constraint_table.yaml`

内容说明：该表定义 Architecture Generator 的硬约束，如 warp mask width、allowed enum、platform bound 等。它在 contract freeze 前筛掉不合法候选。

具体例子：请求 warp size 33 时，active mask width 约束会失败，generator 应输出 hard constraint failure。

### `shared/tables/micro_constraint_estimator_table.yaml`

内容说明：该表定义 micro-constraint estimator 使用的估计规则，例如 area、memory pressure、occupancy、register pressure 和 bandwidth bound。它让 feasibility estimate 可重复。

具体例子：如果 `max_warps_per_sm` 增加，估计器可以据此提高 register pressure bound。

### `shared/tables/mode_decision_table.yaml`

内容说明：该表定义用户请求模式到当前 v5 skill owner 的路由规则，包括 complete spec、vague design、vertical slice、patch request 和 trace debug。它替代旧 mode controller。

具体例子：trace/debug 请求会路由到 Simulation Performance Attribution Engine，而不是旧 closure refinement skill。

### `shared/tables/module_interface_contract_table.yaml`

内容说明：该表定义 RTL module interface 的信号、握手、latency 和 pipeline boundary 规则。它为 Interface Contract Checker 提供检查依据。

具体例子：cache/global interface 可以要求 req/resp tag width 一致，且 response latency 在声明范围内。

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

内容说明：该表定义可绑定的 RTL module 列表及其角色，包括 SM core、warp scheduler、pipeline、register file、scoreboard、LSQ、shared memory 和 cache/global interface。它是 module builder 的目录。

具体例子：minimal SIMT 设计可以启用 `warp_scheduler` 和 `scoreboard`，同时将 tensor unit 标为 absent。

### `shared/tables/rtl_partial_sim_gate_table.yaml`

内容说明：该表定义每类 RTL module 的 partial simulation gate，包括输入 trace、期望输出、golden slice 和失败条件。它让局部仿真标准化。

具体例子：scoreboard gate 可以要求 dependency hazard 出现时 issue 被阻塞，wakeup 后恢复。

### `shared/tables/source_of_truth_generation_table.yaml`

内容说明：该表定义从 `SYSTEM_CONTRACT_IR` 生成或检查派生 artifact 的规则，并声明 docs、RTL defines、tool opcode table 都不能成为 truth source。它防止 artifact drift。

具体例子：ISA opcode table 必须从 `SYSTEM_CONTRACT_IR.isa.opcodes` 派生，不能由 `tools/isa.py` 单独定义。

### `shared/tables/trace_normalization_table.yaml`

内容说明：该表定义不同 trace 来源的字段映射和归一化规则，例如 runtime event、memory event、RTL waveform、golden trace 到统一 schema 的映射。它支撑跨层对比。

具体例子：RTL `valid && ready` transaction 可以归一化成 `memory_request_issued` event。

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

内容说明：该测试 case 文件验证 trace normalizer、bottleneck graph 和 root cause engine 的行为。它要求性能或正确性结论必须有因果链证据。

具体例子：输入缺少 RTL module path 的 trace 时，应期望 `INSUFFICIENT_TRACE_EVIDENCE`。

### `shared/tests/system_contract_golden_engine/cases.yaml`

内容说明：该测试 case 文件验证 System Contract Golden Engine 的 contract freeze、golden semantics coverage 和 duplicate truth rejection。它保护唯一 truth source 规则。

具体例子：case 可以构造 golden model 自行定义 ISA opcode 的情况，并期望 `FORBIDDEN_GOLDEN_TRUTH`。

### `shared/tests/validate_v4_assets.py`

内容说明：这是当前 v5 资产校验脚本，虽然文件名保留 v4 字样，但内容已经验证 v5 self-correcting design-system contract。它检查旧 skill 不回流、shared 只保留 v5 资产、每个文件都有中文说明条目。

具体例子：如果新增 `shared/tables/new_table.yaml` 但没有更新允许列表和 `file_descriptions.zh.md`，脚本会报告 unexpected file 或 missing file description entry。

### `skill_5stage_compression_plan.zh.md`

内容说明：这是中文实施计划文档，记录从 9-stage/4-layer 结构升级为五模块 self-correcting GPGPU design system 的理由、模块职责、缺口补齐、资产创建和迁移策略。它是设计决策背景。

具体例子：维护者想知道为什么 closure 不再是 stage，而是 rewrite loop controller，可以在该计划中找到原始论证。

### `skill_summary.md`

内容说明：这是重写后的中文总览，面向快速阅读者概括当前 v5 skill 系统、五个核心 skill、shared 资产边界、旧 skill 删除状态和验证方式。它比详细计划更短，适合作为日常入口。

具体例子：新 agent 接手任务时，可以先读 `skill_summary.md` 确认当前架构，再按需进入 `file_descriptions.zh.md` 查单个文件用途。

